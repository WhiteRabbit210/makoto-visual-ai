"""
OpenAIプロバイダー
OpenAI APIへの直接接続実装
"""

import os
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime
import asyncio
import aiohttp
import json

from ..interface import (
    AIInterface,
    Message,
    ChatCompletion,
    StreamChunk,
    CompletionOptions,
    MessageRole,
    CompletionUsage,
    FinishReason,
    FunctionCall,
    ToolCall
)
from ...tenant.context import get_current_tenant
from ...tenant.manager import TenantManager, LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(AIInterface):
    """
    OpenAIプロバイダー
    OpenAI APIに直接接続
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1"
    ):
        """
        初期化
        
        Args:
            api_key: OpenAI APIキー
            organization: 組織ID
            base_url: APIベースURL
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.organization = organization or os.environ.get("OPENAI_ORG_ID")
        self.base_url = base_url.rstrip('/')
        
        # テナント設定から取得を試みる
        self._load_from_tenant_config()
    
    def _load_from_tenant_config(self):
        """テナント設定からLLM設定を読み込み"""
        try:
            context = get_current_tenant()
            if context and context.tenant_id:
                manager = TenantManager()
                tenant_info = manager.get_tenant(context.tenant_id)
                
                if tenant_info and tenant_info.config and tenant_info.config.llm_config:
                    llm_config = tenant_info.config.llm_config
                    if llm_config.provider == LLMProvider.OPENAI:
                        # APIキーはSecrets Managerから取得（実装簡略化のため環境変数を使用）
                        if not self.api_key and llm_config.api_key_ref:
                            self.api_key = os.environ.get(llm_config.api_key_ref)
        except Exception as e:
            logger.warning(f"テナント設定の読み込みに失敗: {e}")
    
    def _get_headers(self) -> Dict[str, str]:
        """APIヘッダーを生成"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers
    
    def _convert_finish_reason(self, reason: Optional[str]) -> Optional[FinishReason]:
        """完了理由を変換"""
        if not reason:
            return None
        
        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "function_call": FinishReason.FUNCTION_CALL,
            "tool_calls": FinishReason.TOOL_CALLS,
            "content_filter": FinishReason.CONTENT_FILTER
        }
        return mapping.get(reason, FinishReason.STOP)
    
    def _parse_message(self, msg_data: Dict[str, Any]) -> Message:
        """応答メッセージをパース"""
        message = Message(
            role=MessageRole(msg_data.get("role", "assistant")),
            content=msg_data.get("content")
        )
        
        # Function calling
        if "function_call" in msg_data:
            fc = msg_data["function_call"]
            message.function_call = FunctionCall(
                name=fc.get("name", ""),
                arguments=fc.get("arguments", "")
            )
        
        # Tool calls
        if "tool_calls" in msg_data:
            message.tool_calls = []
            for tc in msg_data["tool_calls"]:
                message.tool_calls.append(ToolCall(
                    id=tc.get("id", ""),
                    type=tc.get("type", "function"),
                    function=FunctionCall(
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", "")
                    )
                ))
        
        return message
    
    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        options: Optional[CompletionOptions] = None
    ) -> ChatCompletion:
        """
        チャット完了を生成
        """
        if not self.api_key:
            raise ValueError("OpenAI APIキーが必要です")
        
        options = options or CompletionOptions()
        url = f"{self.base_url}/chat/completions"
        
        # リクエストボディ構築
        body = {
            "model": model,
            "messages": self.format_messages(messages),
            "temperature": options.temperature,
            "max_tokens": options.max_tokens,
            "top_p": options.top_p,
            "frequency_penalty": options.frequency_penalty,
            "presence_penalty": options.presence_penalty,
            "n": options.n,
            "stream": False
        }
        
        # オプションパラメータ
        if options.stop:
            body["stop"] = options.stop
        if options.user:
            body["user"] = options.user
        if options.seed is not None:
            body["seed"] = options.seed
        if options.logprobs is not None:
            body["logprobs"] = options.logprobs
        if options.functions:
            body["functions"] = options.functions
        if options.function_call:
            body["function_call"] = options.function_call
        if options.tools:
            body["tools"] = options.tools
        if options.tool_choice:
            body["tool_choice"] = options.tool_choice
        
        # API呼び出し
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_headers(),
                json=body
            ) as response:
                response.raise_for_status()
                data = await response.json()
        
        # 応答をパース
        choice = data["choices"][0]
        message = self._parse_message(choice["message"])
        
        # 使用量情報
        usage = None
        if "usage" in data:
            usage = CompletionUsage(
                prompt_tokens=data["usage"]["prompt_tokens"],
                completion_tokens=data["usage"]["completion_tokens"],
                total_tokens=data["usage"]["total_tokens"]
            )
        
        return ChatCompletion(
            id=data.get("id", ""),
            model=data.get("model", model),
            created=datetime.fromtimestamp(data.get("created", 0)),
            message=message,
            usage=usage,
            finish_reason=self._convert_finish_reason(choice.get("finish_reason")),
            system_fingerprint=data.get("system_fingerprint")
        )
    
    async def chat_completion_stream(
        self,
        messages: List[Message],
        model: str,
        options: Optional[CompletionOptions] = None
    ) -> AsyncIterator[StreamChunk]:
        """
        ストリーミングでチャット完了を生成
        """
        if not self.api_key:
            raise ValueError("OpenAI APIキーが必要です")
        
        options = options or CompletionOptions()
        url = f"{self.base_url}/chat/completions"
        
        # リクエストボディ構築
        body = {
            "model": model,
            "messages": self.format_messages(messages),
            "temperature": options.temperature,
            "max_tokens": options.max_tokens,
            "top_p": options.top_p,
            "frequency_penalty": options.frequency_penalty,
            "presence_penalty": options.presence_penalty,
            "n": options.n,
            "stream": True  # ストリーミング有効化
        }
        
        # オプションパラメータ
        if options.stop:
            body["stop"] = options.stop
        if options.user:
            body["user"] = options.user
        if options.functions:
            body["functions"] = options.functions
        if options.tools:
            body["tools"] = options.tools
        
        # SSEストリーミング
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._get_headers(),
                json=body
            ) as response:
                response.raise_for_status()
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith("data: "):
                        data_str = line[6:]  # "data: "を除去
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            choice = data["choices"][0]
                            
                            # デルタメッセージをパース
                            delta = choice.get("delta", {})
                            delta_message = Message(
                                role=MessageRole(delta.get("role", "assistant")) if "role" in delta else MessageRole.ASSISTANT,
                                content=delta.get("content")
                            )
                            
                            # Function callingのデルタ
                            if "function_call" in delta:
                                fc = delta["function_call"]
                                delta_message.function_call = FunctionCall(
                                    name=fc.get("name", ""),
                                    arguments=fc.get("arguments", "")
                                )
                            
                            # Tool callsのデルタ
                            if "tool_calls" in delta:
                                delta_message.tool_calls = []
                                for tc in delta["tool_calls"]:
                                    delta_message.tool_calls.append(ToolCall(
                                        id=tc.get("id", ""),
                                        type=tc.get("type", "function"),
                                        function=FunctionCall(
                                            name=tc.get("function", {}).get("name", ""),
                                            arguments=tc.get("function", {}).get("arguments", "")
                                        )
                                    ))
                            
                            # ストリームチャンクを生成
                            yield StreamChunk(
                                id=data.get("id", ""),
                                model=data.get("model", model),
                                created=datetime.fromtimestamp(data.get("created", 0)),
                                delta=delta_message,
                                finish_reason=self._convert_finish_reason(choice.get("finish_reason"))
                            )
                            
                        except json.JSONDecodeError:
                            logger.warning(f"JSONパースエラー: {data_str}")
                            continue
    
    async def count_tokens(
        self,
        messages: List[Message],
        model: str
    ) -> int:
        """
        トークン数をカウント
        簡易実装（実際にはtiktokenライブラリを使用すべき）
        """
        # 簡易的な推定（4文字 = 1トークン）
        total_chars = 0
        for msg in messages:
            if msg.content:
                total_chars += len(msg.content)
            if msg.function_call:
                total_chars += len(msg.function_call.name)
                total_chars += len(msg.function_call.arguments)
        
        return total_chars // 4
    
    def get_available_models(self) -> List[str]:
        """
        利用可能なモデル一覧を取得
        """
        return [
            "gpt-4-turbo-preview",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-3.5-turbo-1106"
        ]
    
    def validate_model(self, model: str) -> bool:
        """
        モデルが利用可能か確認
        """
        # GPTモデルであれば許可
        return model.startswith(("gpt-4", "gpt-3.5"))