"""
AIインターフェース
異なるLLMプロバイダーを統一的に扱うための抽象化
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator, Union
from datetime import datetime
import json


class MessageRole(Enum):
    """メッセージロール"""
    SYSTEM = "system"  # システムメッセージ
    USER = "user"  # ユーザーメッセージ
    ASSISTANT = "assistant"  # AIアシスタントメッセージ
    FUNCTION = "function"  # 関数呼び出し結果
    TOOL = "tool"  # ツール呼び出し結果


class FinishReason(Enum):
    """完了理由"""
    STOP = "stop"  # 通常終了
    LENGTH = "length"  # 最大長に到達
    FUNCTION_CALL = "function_call"  # 関数呼び出し
    TOOL_CALLS = "tool_calls"  # ツール呼び出し
    CONTENT_FILTER = "content_filter"  # コンテンツフィルタ


@dataclass
class FunctionCall:
    """
    関数呼び出し
    Function Callingの情報
    """
    name: str  # 関数名
    arguments: str  # 引数（JSON文字列）
    
    def parse_arguments(self) -> Dict[str, Any]:
        """引数をパース"""
        try:
            return json.loads(self.arguments)
        except (json.JSONDecodeError, TypeError):
            return {}


@dataclass
class ToolCall:
    """
    ツール呼び出し
    Tools APIの情報
    """
    id: str  # ツールID
    type: str  # ツールタイプ（通常"function"）
    function: FunctionCall  # 関数情報


@dataclass
class Message:
    """
    チャットメッセージ
    プロバイダー間で共通のメッセージ形式
    """
    role: MessageRole  # ロール
    content: Optional[str] = None  # メッセージ内容
    name: Optional[str] = None  # 送信者名（オプション）
    function_call: Optional[FunctionCall] = None  # 関数呼び出し
    tool_calls: Optional[List[ToolCall]] = None  # ツール呼び出し
    tool_call_id: Optional[str] = None  # ツール呼び出しID（結果返却時）
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        result = {"role": self.role.value}
        if self.content is not None:
            result["content"] = self.content
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = {
                "name": self.function_call.name,
                "arguments": self.function_call.arguments
            }
        if self.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class CompletionUsage:
    """
    トークン使用量
    API使用量の統計情報
    """
    prompt_tokens: int  # プロンプトトークン数
    completion_tokens: int  # 生成トークン数
    total_tokens: int  # 合計トークン数
    
    @classmethod
    def create(cls, prompt_tokens: int, completion_tokens: int) -> 'CompletionUsage':
        """使用量を作成"""
        return cls(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens
        )


@dataclass
class ChatCompletion:
    """
    チャット完了応答
    プロバイダー間で共通の応答形式
    """
    id: str  # 応答ID
    model: str  # 使用モデル
    created: datetime  # 作成日時
    message: Message  # 応答メッセージ
    usage: Optional[CompletionUsage] = None  # 使用量
    finish_reason: Optional[FinishReason] = None  # 完了理由
    system_fingerprint: Optional[str] = None  # システムフィンガープリント
    
    @property
    def content(self) -> Optional[str]:
        """メッセージ内容を直接取得"""
        return self.message.content if self.message else None
    
    @property
    def has_function_call(self) -> bool:
        """関数呼び出しがあるか"""
        return self.message and self.message.function_call is not None
    
    @property
    def has_tool_calls(self) -> bool:
        """ツール呼び出しがあるか"""
        return self.message and self.message.tool_calls is not None


@dataclass
class StreamChunk:
    """
    ストリーミングチャンク
    ストリーミング応答の一部
    """
    id: str  # チャンクID
    model: str  # 使用モデル
    created: datetime  # 作成日時
    delta: Message  # 差分メッセージ
    finish_reason: Optional[FinishReason] = None  # 完了理由
    usage: Optional[CompletionUsage] = None  # 使用量（最後のチャンク）
    
    @property
    def content(self) -> Optional[str]:
        """デルタ内容を直接取得"""
        return self.delta.content if self.delta else None
    
    @property
    def is_final(self) -> bool:
        """最後のチャンクか"""
        return self.finish_reason is not None


@dataclass
class CompletionOptions:
    """
    生成オプション
    LLMの生成パラメータ
    """
    temperature: float = 0.7  # 温度（ランダム性）
    max_tokens: Optional[int] = None  # 最大トークン数
    top_p: float = 1.0  # Top-pサンプリング
    frequency_penalty: float = 0.0  # 頻度ペナルティ
    presence_penalty: float = 0.0  # 存在ペナルティ
    stop: Optional[List[str]] = None  # 停止シーケンス
    n: int = 1  # 生成数
    stream: bool = False  # ストリーミング有効化
    logprobs: Optional[int] = None  # ログ確率を含める
    echo: bool = False  # プロンプトをエコー
    user: Optional[str] = None  # ユーザー識別子
    seed: Optional[int] = None  # シード値（再現性）
    
    # Function Calling
    functions: Optional[List[Dict[str, Any]]] = None  # 利用可能関数
    function_call: Optional[Union[str, Dict[str, str]]] = None  # 関数呼び出し制御
    tools: Optional[List[Dict[str, Any]]] = None  # 利用可能ツール
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None  # ツール選択制御
    
    # プロバイダー固有
    metadata: Dict[str, Any] = field(default_factory=dict)  # プロバイダー固有設定


class AIInterface(ABC):
    """
    AIプロバイダーインターフェース
    各プロバイダーが実装すべき基本インターフェース
    """
    
    @abstractmethod
    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        options: Optional[CompletionOptions] = None
    ) -> ChatCompletion:
        """
        チャット完了を生成
        
        Args:
            messages: メッセージ履歴
            model: 使用モデル
            options: 生成オプション
            
        Returns:
            チャット完了応答
        """
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[Message],
        model: str,
        options: Optional[CompletionOptions] = None
    ) -> AsyncIterator[StreamChunk]:
        """
        ストリーミングでチャット完了を生成
        
        Args:
            messages: メッセージ履歴
            model: 使用モデル
            options: 生成オプション
            
        Yields:
            ストリーミングチャンク
        """
        pass
    
    @abstractmethod
    async def count_tokens(
        self,
        messages: List[Message],
        model: str
    ) -> int:
        """
        トークン数をカウント
        
        Args:
            messages: メッセージ履歴
            model: 使用モデル
            
        Returns:
            トークン数
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        利用可能なモデル一覧を取得
        
        Returns:
            モデル名のリスト
        """
        pass
    
    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """
        モデルが利用可能か確認
        
        Args:
            model: モデル名
            
        Returns:
            利用可能な場合True
        """
        pass
    
    def format_messages(
        self,
        messages: List[Message]
    ) -> List[Dict[str, Any]]:
        """
        メッセージをプロバイダー形式に変換
        
        Args:
            messages: メッセージリスト
            
        Returns:
            プロバイダー形式のメッセージ
        """
        return [msg.to_dict() for msg in messages]
    
    async def test_connection(self) -> bool:
        """
        接続テスト
        
        Returns:
            接続成功の場合True
        """
        try:
            # 簡単なテストメッセージを送信
            test_messages = [
                Message(role=MessageRole.USER, content="Hello")
            ]
            models = self.get_available_models()
            if models:
                await self.chat_completion(
                    messages=test_messages,
                    model=models[0],
                    options=CompletionOptions(max_tokens=10)
                )
                return True
        except Exception:
            pass
        return False