from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from services.chat_service import ChatService
from services.image_generation_service import image_generation_service
from services.web_crawler_service import web_crawler_service
from openai import AzureOpenAI
import os
import asyncio
import time
from dotenv import load_dotenv
import json
from utils.logger import log_api_request, log_api_response, log_chat_request, log_chat_response, log_error, measure_time, log_chat_performance

# ドキュメント準拠の型定義をインポート
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from backend_types.api_types import (
        ChatMessage, ChatRoom, CreateChatRequest, CreateChatResponse,
        GetChatsParams, GetChatsResponse, ChatStreamRequest, StreamMessage,
        TextChunkEvent, ImageGeneratingEvent, ImageGeneratedEvent,
        StreamCompleteEvent, StreamErrorEvent, generate_uuid, get_current_datetime
    )
except ImportError:
    # フォールバック（型定義ファイルがまだ存在しない場合）
    pass

load_dotenv()

router = APIRouter()

# ロガーの設定
import logging
logger = logging.getLogger('chat')

# Azure OpenAIクライアントを初期化
try:
    azure_client = AzureOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
except Exception as e:
    print(f"Azure OpenAI設定エラー: {e}")
    azure_client = None

# Models
class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    room_id: Optional[str] = None  # chat_idからroom_idに変更

class ChatCompletionRequest(BaseModel):
    messages: List[StreamMessage]
    model: str = "gpt-4"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False
    modes: Optional[List[str]] = []  # active_modes から modes に変更
    room_id: Optional[str] = None  # chat_idからroom_idに変更
    search_keywords: Optional[List[str]] = None  # エージェントが提供する検索キーワード

class ChatCompletionResponse(BaseModel):
    message: ChatMessage
    usage: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    room_id: str  # chat_idからroom_idに変更
    message: Dict[str, Any]
    response: Dict[str, Any]

class Chat(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    last_message: Optional[str] = None
    messages: Optional[List[Dict[str, Any]]] = None

# 画像生成リクエストモデル
class ImageGenerationRequest(BaseModel):
    prompt: str
    n: int = 1
    size: str = "1024x1024"
    quality: str = "medium"
    output_format: str = "url"

# 画像生成レスポンスモデル
class ImageGenerationResponse(BaseModel):
    success: bool
    images: List[Dict[str, Any]] = []
    error: Optional[str] = None
    prompt: Optional[str] = None


@router.get("/chats")
async def get_chats(
    page_size: int = 50,
    next_key: Optional[str] = None,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """チャット一覧を取得（カーソルベースページネーション）
    
    Args:
        page_size: 1ページあたりの件数（デフォルト50、最大100）
        next_key: 次ページ用のカーソルキー（初回はNone）
        tenant_id: テナントID
        user_id: ユーザーID
    
    Returns:
        {
            "chats": チャットリスト,
            "has_more": まだデータがあるか,
            "next_key": 次ページ用のキー
        }
    """
    result = await ChatService.get_all_chats(
        tenant_id=tenant_id,
        user_id=user_id,
        limit=page_size,
        last_evaluated_key=next_key
    )
    
    return result

@router.get("/chats/{room_id}")
async def get_chat(
    room_id: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user",
    limit: int = 50
):
    """特定のチャットを取得
    
    Args:
        room_id: チャットルームID
        tenant_id: テナントID
        user_id: ユーザーID
        limit: メッセージ取得件数
    """
    chat = ChatService.get_chat(
        room_id=room_id,
        tenant_id=tenant_id,
        user_id=user_id,
        limit=limit
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    request: ChatRequest,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """新しいチャットを作成または既存に追加"""
    # Create or get chat
    if request.room_id:
        chat = ChatService.get_chat(
            room_id=request.room_id,
            tenant_id=tenant_id,
            user_id=user_id
        )
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        room_id = request.room_id
    else:
        title = request.message[:50] + "..." if len(request.message) > 50 else request.message
        chat = await ChatService.create_chat(
            title=title,
            tenant_id=tenant_id,
            user_id=user_id
        )
        room_id = chat['id']
    
    # Add user message
    user_message = await ChatService.add_message(
        room_id=room_id,
        role="user",
        content=request.message,
        tenant_id=tenant_id,
        user_id=user_id
    )
    
    try:
        if not azure_client:
            raise HTTPException(status_code=500, detail="Azure OpenAIクライアントが初期化されていません")
        
        # API呼び出し
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=[
                {"role": "system", "content": "あなたは日本語で回答する親切なAIアシスタントです。"},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        ai_content = response.choices[0].message.content
        ai_message = await ChatService.add_message(
            room_id=room_id,
            role="assistant",
            content=ai_content,
            tenant_id=tenant_id,
            user_id=user_id
        )
    except Exception as e:
        ai_content = f"エラーが発生しました: {str(e)}"
        ai_message = await ChatService.add_message(
            room_id=room_id,
            role="assistant",
            content=ai_content,
            tenant_id=tenant_id,
            user_id=user_id
        )
    
    return ChatResponse(
        room_id=room_id,
        message=user_message,
        response=ai_message
    )

@router.delete("/chats/{room_id}")
async def delete_chat(
    room_id: str,
    tenant_id: str = "default_tenant",
    user_id: str = "default_user"
):
    """チャットを削除"""
    chat = ChatService.get_chat(
        room_id=room_id,
        tenant_id=tenant_id,
        user_id=user_id
    )
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    await ChatService.delete_chat(
        room_id=room_id,
        tenant_id=tenant_id,
        user_id=user_id
    )
    return {"message": "Chat deleted successfully"}

@router.post("/chat/completion", response_model=ChatCompletionResponse)
async def chat_completion(request: ChatCompletionRequest):
    """
    ChatGPTにメッセージを送信して応答を取得する
    """
    # リクエストログ
    log_api_request("/api/chat/completion", "POST", {
        "messages_count": len(request.messages),
        "modes": request.modes,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    })
    
    # 最新のユーザーメッセージをログ
    if request.messages:
        last_msg = request.messages[-1]
        if last_msg.role == "user":
            log_chat_request(last_msg.content, request.modes)
    
    try:
        if not azure_client:
            raise HTTPException(status_code=500, detail="Azure OpenAIクライアントが初期化されていません")
        
        # OpenAI APIに送信するメッセージ形式に変換
        api_messages = []
        
        # システムメッセージを追加
        import pytz
        
        # 日本時間を取得
        japan_tz = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(japan_tz)
        
        # プレースホルダーを実際の値に置換
        system_message = f"""あなたは日本語で回答する親切なAIアシスタントです。

現在の情報:
- 今日の日付: {current_time.strftime('%Y年%m月%d日')}
- 現在時刻: {current_time.strftime('%H時%M分')}
- 曜日: {['月', '火', '水', '木', '金', '土', '日'][current_time.weekday()]}曜日
- 年: {current_time.year}年
- 月: {current_time.month}月
- 日: {current_time.day}日"""
        
        # エージェントモードの処理
        search_keywords = []
        crawl_sources = []
        
        if request.modes and "agent" in request.modes:
            # エージェントによる分析
            if request.messages:
                last_user_msg = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
                if last_user_msg:
                    # エージェントAPIを直接呼び出し
                    from .agent import analyze_prompt, AnalyzeRequest
                    
                    agent_request = AnalyzeRequest(
                        prompt=last_user_msg.content,
                        context=[{"role": msg.role, "content": msg.content} for msg in request.messages[-6:]]
                    )
                    analysis_result = await analyze_prompt(agent_request)
                    
                    # Webモードが推奨された場合
                    for mode in analysis_result.modes:
                        if mode.type == "web" and mode.confidence > 0.5 and mode.search_keywords:
                            search_keywords = mode.search_keywords
                            # Webクロールを実行
                            crawl_result = await web_crawler_service.search_and_crawl(
                                keywords=search_keywords,
                                original_query=last_user_msg.content
                            )
                            
                            if crawl_result.get('success'):
                                crawl_sources = crawl_result.get('sources', [])
                                if crawl_result.get('summary'):
                                    system_message += f"\n\n## Web検索結果\n以下の最新情報を参考にして回答してください：\n{crawl_result['summary']}\n\n必ず回答の最後に参照元のURLを「参考サイト」として箇条書きで記載してください。"
                            break
        
        # アクティブモードに応じてシステムメッセージを調整
        if request.modes and "webcrawl" in request.modes and not search_keywords:
            system_message += "\n\nWebクロールモードが有効です。必要に応じてWeb上の情報を参照してください。"
        if request.modes and "image" in request.modes:
            system_message += "\n\n画像生成モードが有効です。ユーザーが画像生成を要求した場合は、画像の説明のみを提供し、実際の画像URLやMarkdown形式の画像リンクは含めないでください。画像は別途システムが生成します。"
        if request.modes and "rag" in request.modes:
            system_message += "\n\nRAGモードが有効です。文書検索を活用した回答を提供してください。"
        
        api_messages.append({"role": "system", "content": system_message})
        
        # ユーザーメッセージを追加
        for msg in request.messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Azure OpenAI APIを呼び出し
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
            messages=api_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=False
        )
        
        # レスポンスを構築
        assistant_message = response.choices[0].message.content
        
        chat_response = ChatCompletionResponse(
            message=ChatMessage(
                role="assistant",
                content=assistant_message,
                timestamp=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            ),
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        )
        
        log_chat_response(assistant_message, chat_response.usage)
        log_api_response("/api/chat/completion", 200)
        return chat_response
        
    except Exception as e:
        log_error("ChatGPT API Error", str(e), "/api/chat/completion")
        raise HTTPException(status_code=500, detail=f"ChatGPT API呼び出しエラー: {str(e)}")

@router.post("/chat/stream")
async def chat_stream(request: ChatCompletionRequest):
    """
    ストリーミング形式でChatGPTの応答を取得する
    """
    # 処理時間計測開始
    start_time = time.time()
    performance_breakdown = {
        'request_processing': 0.0,
        'system_message_creation': 0.0,
        'agent_analysis': 0.0,
        'web_search': 0.0,
        'llm_api_call': 0.0,
        'first_chunk': 0.0,
        'full_streaming': 0.0,
        'message_save': 0.0,
        'total': 0.0
    }
    
    # リクエスト処理開始
    request_start = time.time()
    
    # リクエストログ
    log_api_request("/api/chat/stream", "POST", {
        "messages_count": len(request.messages),
        "modes": request.modes,
        "stream": True
    })
    
    # 最新のユーザーメッセージをログ
    if request.messages:
        last_msg = request.messages[-1]
        if last_msg.role == "user":
            log_chat_request(last_msg.content, request.modes)
    
    performance_breakdown['request_processing'] = time.time() - request_start
    logger.info(f"リクエスト処理時間: {performance_breakdown['request_processing']:.3f}秒")
    
    try:
        if not azure_client:
            raise HTTPException(status_code=500, detail="Azure OpenAIクライアントが初期化されていません")
        
        # OpenAI APIに送信するメッセージ形式に変換
        api_messages = []
        
        # システムメッセージを追加
        system_message_start = time.time()
        import pytz
        
        # 日本時間を取得
        japan_tz = pytz.timezone('Asia/Tokyo')
        current_time = datetime.now(japan_tz)
        
        # プレースホルダーを実際の値に置換
        system_message = f"""あなたは日本語で回答する親切なAIアシスタントです。

現在の情報:
- 今日の日付: {current_time.strftime('%Y年%m月%d日')}
- 現在時刻: {current_time.strftime('%H時%M分')}
- 曜日: {['月', '火', '水', '木', '金', '土', '日'][current_time.weekday()]}曜日
- 年: {current_time.year}年
- 月: {current_time.month}月
- 日: {current_time.day}日"""
        
        
        performance_breakdown['system_message_creation'] = time.time() - system_message_start
        # エージェントモードの処理
        search_keywords = []
        crawl_sources = []
        analysis_result = None
        
        if request.modes and "agent" in request.modes:
            # エージェントによる分析
            agent_start = time.time()
            logger.info("エージェント分析開始")
            if request.messages:
                last_user_msg = next((msg for msg in reversed(request.messages) if msg.role == "user"), None)
                if last_user_msg:
                    # エージェントAPIを直接呼び出し
                    from .agent import analyze_prompt, AnalyzeRequest
                    
                    agent_request = AnalyzeRequest(
                        prompt=last_user_msg.content,
                        context=[{"role": msg.role, "content": msg.content} for msg in request.messages[-6:]]
                    )
                    analysis_result = await analyze_prompt(agent_request)
                    performance_breakdown['agent_analysis'] = time.time() - agent_start
                    logger.info(f"エージェント分析完了: {performance_breakdown['agent_analysis']:.3f}秒")
                    
                    # Webモードが推奨された場合
                    for mode in analysis_result.modes:
                        if mode.type == "web" and mode.confidence > 0.5 and mode.search_keywords:
                            search_keywords = mode.search_keywords
                            # Webクロールを実行
                            web_search_start = time.time()
                            logger.info(f"Web検索開始: キーワード = {search_keywords}")
                            crawl_result = await web_crawler_service.search_and_crawl(
                                keywords=search_keywords,
                                original_query=last_user_msg.content
                            )
                            
                            if crawl_result.get('success'):
                                crawl_sources = crawl_result.get('sources', [])
                                if crawl_result.get('summary'):
                                    system_message += f"\n\n## Web検索結果\n以下の最新情報を参考にして回答してください：\n{crawl_result['summary']}\n\n必ず回答の最後に参照元のURLを「参考サイト」として箇条書きで記載してください。"
                            performance_breakdown['web_search'] = time.time() - web_search_start
                            logger.info(f"Web検索完了: {performance_breakdown['web_search']:.3f}秒")
                            break
        
        # アクティブモードに応じてシステムメッセージを調整
        if request.modes and "webcrawl" in request.modes and not search_keywords:
            system_message += "\n\nWebクロールモードが有効です。必要に応じてWeb上の情報を参照してください。"
        if request.modes and "image" in request.modes:
            system_message += "\n\n画像生成モードが有効です。ユーザーが画像生成を要求した場合は、画像の説明のみを提供し、実際の画像URLやMarkdown形式の画像リンクは含めないでください。画像は別途システムが生成します。"
        if request.modes and "rag" in request.modes:
            system_message += "\n\nRAGモードが有効です。文書検索を活用した回答を提供してください。"
        
        api_messages.append({"role": "system", "content": system_message})
        
        # ユーザーメッセージを追加
        for msg in request.messages:
            api_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # ストリーミング形式でAzure OpenAI APIを呼び出し
        llm_api_start = time.time()
        logger.info("LLM API呼び出し開始")
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
            messages=api_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=True
        )
        performance_breakdown['llm_api_call'] = time.time() - llm_api_start
        logger.info(f"LLM API呼び出し完了: {performance_breakdown['llm_api_call']:.3f}秒")
        
        # ストリーミング形式でレスポンスを返す
        async def generate():
            # パフォーマンス計測とログ出力
            mode_type = "agent" if request.modes and "agent" in request.modes else "normal"
            streaming_start = time.time()
            first_chunk_received = False
            
            # 外部スコープの変数を参照
            nonlocal crawl_sources, search_keywords, performance_breakdown, start_time, analysis_result
            
            # 処理完了後のログ出力用
            def log_final_performance():
                performance_breakdown['total'] = time.time() - start_time
                
                # 詳細な内訳をログに出力
                from utils.logger import log_chat_performance
                log_chat_performance(
                    mode=mode_type,
                    total_time=performance_breakdown['total'],
                    breakdown={
                        'リクエスト処理': performance_breakdown['request_processing'],
                        'システムメッセージ作成': performance_breakdown['system_message_creation'],
                        'エージェント分析': performance_breakdown['agent_analysis'],
                        'Web検索': performance_breakdown['web_search'],
                        'LLM API呼び出し': performance_breakdown['llm_api_call'],
                        '最初のチャンク受信': performance_breakdown['first_chunk'],
                        'ストリーミング全体': performance_breakdown['full_streaming'],
                        'メッセージ保存': performance_breakdown['message_save']
                    }
                )
            import re
            full_response = ""
            # 画像URLパターン（Markdown形式）を検出する正規表現
            image_pattern = re.compile(r'!\[.*?\]\([^)]+\)')
            
            # エージェントステータス送信用のヘルパー関数
            async def send_agent_status(status_type: str, message: str, details: dict = None):
                """汎用的なエージェントステータス送信"""
                status_data = {
                    'type': 'agent_status',
                    'status': status_type,
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'details': details or {}
                }
                yield f"data: {json.dumps(status_data, ensure_ascii=False)}\n\n"
            
            # エージェントの思考を送信する関数
            async def send_agent_thought(thought: str, status: str = 'thinking'):
                """エージェントの思考過程を送信"""
                thought_data = {
                    'type': 'agent_thought',
                    'content': thought,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(thought_data, ensure_ascii=False)}\n\n"
            
            # エージェントモードのステータス送信
            if request.modes and "agent" in request.modes:
                # 分析開始
                async for data in send_agent_status('analyzing', 'エージェントが分析中...', {
                    'description': '最適な回答方法を検討しています'
                }):
                    yield data
                
                # 思考過程を送信（分析結果に基づく）
                if analysis_result and hasattr(analysis_result, 'modes'):
                    # 分析結果の思考を送信
                    if hasattr(analysis_result, 'analysis') and analysis_result.analysis:
                        async for data in send_agent_thought(analysis_result.analysis, 'analyzing'):
                            yield data
                        await asyncio.sleep(0.3)
                    
                    # 有効なモードの判定理由を送信
                    for mode in analysis_result.modes:
                        if mode.confidence > 0.5 and mode.type != 'none':
                            thought = f"{mode.reason}（信頼度: {int(mode.confidence * 100)}%）"
                            if mode.type == 'web' and mode.search_keywords:
                                thought += f"\n検索キーワード: {', '.join(mode.search_keywords)}"
                            
                            async for data in send_agent_thought(thought, 'analyzing'):
                                yield data
                            await asyncio.sleep(0.2)
                
                # Web検索実行中
                if crawl_sources and search_keywords:
                    async for data in send_agent_thought(f"「{', '.join(search_keywords)}」でWeb検索を実行中...", 'searching'):
                        yield data
                    
                    async for data in send_agent_status('searching', 'Webから情報を検索中...', {
                        'keywords': search_keywords,
                        'description': f'「{", ".join(search_keywords)}」を検索しています'
                    }):
                        yield data
                    await asyncio.sleep(0.5)  # UIの更新のため少し待機
                    
                    # クロール中
                    async for data in send_agent_thought(f"{len(crawl_sources)}件のWebサイトから情報を収集しました。", 'searching'):
                        yield data
                    
                    async for data in send_agent_status('crawling', 'ページを収集中...', {
                        'count': len(crawl_sources),
                        'description': f'{len(crawl_sources)}サイトから情報を取得しました'
                    }):
                        yield data
                    await asyncio.sleep(0.5)
            
            for chunk in response:
                if not first_chunk_received:
                    performance_breakdown['first_chunk'] = time.time() - streaming_start
                    logger.info(f"最初のチャンク受信: {performance_breakdown['first_chunk']:.3f}秒")
                    first_chunk_received = True
                
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and hasattr(delta, 'content') and delta.content:
                        content = delta.content
                        
                        # 画像生成モードが有効な場合、画像URLパターンを除去
                        if request.modes and "image" in request.modes:
                            content = image_pattern.sub('', content)
                        
                        full_response += delta.content  # 元のコンテンツを保存（ログ用）
                        if content:  # 除去後にコンテンツが残っている場合のみ送信
                            yield f"data: {json.dumps({'content': content})}\n\n"
            
            # ストリーミング完了
            performance_breakdown['full_streaming'] = time.time() - streaming_start
            logger.info(f"ストリーミング完了: {performance_breakdown['full_streaming']:.3f}秒")
            
            # ストリーミング完了時にメッセージを保存
            try:
                # ルームIDを取得または作成
                room_id = request.room_id
                
                # ユーザーメッセージを取得
                user_messages = [msg for msg in request.messages if msg.role == "user"]
                last_user_message = user_messages[-1] if user_messages else None
                
                if not room_id and last_user_message:
                    # 新しいチャットを作成
                    title = last_user_message.content[:50] + "..." if len(last_user_message.content) > 50 else last_user_message.content
                    chat = ChatService.create_chat(title)
                    room_id = chat['id']
                    
                    # ユーザーメッセージを保存
                    ChatService.add_message(room_id, "user", last_user_message.content)
                elif room_id and last_user_message:
                    # 既存のチャットにユーザーメッセージを追加
                    ChatService.add_message(room_id, "user", last_user_message.content)
                
                # まずAIメッセージを保存（画像はプレースホルダー付き）
                assistant_message = None
                if room_id and full_response:
                    # 画像生成モードの場合はプレースホルダーを準備
                    placeholder_images = []
                    if request.modes and "image" in request.modes and last_user_message:
                        # プレースホルダー画像を作成
                        import uuid
                        image_id = str(uuid.uuid4())
                        placeholder_images = [{
                            "url": f"placeholder://image/{room_id}/{image_id}",
                            "status": "generating",
                            "prompt": last_user_message.content
                        }]
                    
                    # メッセージサイズをチェック
                    message_size = len(full_response.encode('utf-8'))
                    log_chat_response(f"Message size: {message_size} bytes", {"size_check": True})
                    
                    # Webクロール結果をメッセージに追加
                    crawl_sources_for_message = crawl_sources if crawl_sources else None
                    
                    # メッセージを保存（プレースホルダー付き）
                    message_save_start = time.time()
                    assistant_message = ChatService.add_message(
                        room_id, 
                        "assistant", 
                        full_response, 
                        placeholder_images if placeholder_images else None,
                        crawl_sources_for_message
                    )
                    performance_breakdown['message_save'] = time.time() - message_save_start
                    logger.info(f"メッセージ保存完了: {performance_breakdown['message_save']:.3f}秒")
                    log_chat_response(full_response[:100], {"saved": True, "room_id": room_id, "message_id": assistant_message['id'], "size_bytes": message_size})
                    
                    # 画像生成モードが有効な場合は画像を生成
                    if request.modes and "image" in request.modes and last_user_message and assistant_message:
                        # ユーザーのメッセージを画像生成プロンプトとして使用
                        image_prompt = last_user_message.content
                        
                        # 画像を生成
                        try:
                            yield f"data: {json.dumps({'generating_image': True})}\n\n"
                            
                            image_result = await image_generation_service.generate_image(
                                prompt=image_prompt,
                                size="1024x1024",
                                quality="medium"
                            )
                            
                            if image_result and image_result.get('success'):
                                images = image_result.get('images', [])
                                if images:
                                    # 画像URLを送信
                                    yield f"data: {json.dumps({'images': images})}\n\n"
                                    
                                    # メッセージの画像を更新
                                    ChatService.update_message_images(assistant_message['id'], images)
                                    log_api_response("/api/chat/stream", 200, {"image_generated": True, "message_updated": True})
                            else:
                                error_msg = image_result.get('error', 'Unknown error') if image_result else 'Image generation failed'
                                yield f"data: {json.dumps({'image_error': error_msg})}\n\n"
                                
                                # エラー時はプレースホルダーをエラー状態に更新
                                error_images = [{
                                    "url": f"placeholder://image/{room_id}/{image_id}",
                                    "status": "error",
                                    "error": error_msg,
                                    "prompt": last_user_message.content
                                }]
                                ChatService.update_message_images(assistant_message['id'], error_images)
                                log_error("画像生成失敗", error_msg, "/api/chat/stream")
                        except Exception as e:
                            log_error("画像生成エラー", str(e), "/api/chat/stream")
                            yield f"data: {json.dumps({'image_error': str(e)})}\n\n"
                            
                            # エラー時はプレースホルダーをエラー状態に更新
                            error_images = [{
                                "url": f"placeholder://image/{room_id}/{image_id}",
                                "status": "error",
                                "error": str(e),
                                "prompt": last_user_message.content
                            }]
                            ChatService.update_message_images(assistant_message['id'], error_images)
                
                # エージェント処理完了
                if request.modes and "agent" in request.modes:
                    async for data in send_agent_status('complete', '処理完了', None):
                        yield data
                
                # 新規チャットの場合、タイトルを自動生成
                is_new_chat = not request.room_id
                if is_new_chat and last_user_message and full_response and room_id:
                    # ユーザーメッセージが短い場合はそのまま使用
                    if len(last_user_message.content) <= 30:
                        new_title = last_user_message.content
                    else:
                        # 長い場合は最初の30文字 + ...
                        new_title = last_user_message.content[:30] + "..."
                    
                    # タイトルを更新
                    ChatService.update_chat_title(room_id, new_title)
                    logger.info(f"チャットタイトル更新: {room_id} -> {new_title}")
                
                # ルームIDとクロール結果をクライアントに送信
                done_data = {'done': True, 'room_id': room_id}
                if crawl_sources:
                    done_data['crawl_sources'] = crawl_sources
                yield f"data: {json.dumps(done_data)}\n\n"
                
                # パフォーマンスログ出力
                log_final_performance()
            except Exception as e:
                log_error("メッセージ保存エラー", str(e), "/api/chat/stream")
                yield f"data: {json.dumps({'done': True})}\n\n"
                # パフォーマンスログ出力（エラー時）
                log_final_performance()
        
        log_api_response("/api/chat/stream", 200, {"streaming": True})
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        log_error("ChatGPT Streaming Error", str(e), "/api/chat/stream")
        raise HTTPException(status_code=500, detail=f"ChatGPT API呼び出しエラー: {str(e)}")

@router.post("/images/generate", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    """
    Azure OpenAI DALL-E 3を使用して画像を生成する
    """
    # リクエストログ
    log_api_request("/api/images/generate", "POST", {
        "prompt": request.prompt[:50],
        "size": request.size,
        "quality": request.quality,
        "output_format": request.output_format
    })
    
    try:
        # 画像生成サービスを呼び出し
        result = await image_generation_service.generate_image(
            prompt=request.prompt,
            n=request.n,
            size=request.size,
            quality=request.quality,
            output_format=request.output_format
        )
        
        if result and result.get('success'):
            response = ImageGenerationResponse(
                success=True,
                images=result.get('images', []),
                prompt=result.get('prompt')
            )
            
            log_api_response("/api/images/generate", 200, {
                "images_count": len(response.images),
                "prompt": request.prompt[:50]
            })
            
            return response
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'Image generation service not available'
            response = ImageGenerationResponse(
                success=False,
                error=error_msg,
                prompt=request.prompt
            )
            
            log_error("Image Generation Error", error_msg, "/api/images/generate")
            return response
            
    except Exception as e:
        log_error("Image Generation Exception", str(e), "/api/images/generate")
        return ImageGenerationResponse(
            success=False,
            error=f"画像生成エラー: {str(e)}",
            prompt=request.prompt
        )