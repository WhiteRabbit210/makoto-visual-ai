"""
API型定義（Python版）

このファイルはドキュメント（/makoto/docs/仕様書/型定義/）に
完全準拠した型定義です。

変更する場合は必ずドキュメントを先に更新してください。
"""

from typing import Optional, List, Dict, Literal, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ============================================
# 基本型
# ============================================

UUID = str
DateTime = str  # ISO 8601形式

# ============================================
# チャットAPI型定義
# ドキュメント: /makoto/docs/仕様書/型定義/チャットAPI型定義.md
# ============================================

# メッセージロール
MessageRole = Literal['user', 'assistant', 'system']

# チャットモード
ChatMode = Literal['chat', 'image', 'web', 'rag']


class LastMessage(BaseModel):
    """最後のメッセージ"""
    content: str
    timestamp: DateTime
    role: str


class ChatSettings(BaseModel):
    """チャット設定"""
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    active_modes: Optional[List[str]] = None


class ChatRoom(BaseModel):
    """チャットルーム"""
    # 識別子
    room_id: str
    user_id: str
    
    # 基本情報
    title: str
    created_at: DateTime
    updated_at: DateTime
    
    # 統計情報
    message_count: int
    last_message: Optional[LastMessage] = None
    
    # 設定
    settings: Optional[ChatSettings] = None


class RAGSource(BaseModel):
    """RAGソース"""
    title: str
    source: str
    content: str
    score: float = Field(ge=0.0, le=1.0)


class RAGContext(BaseModel):
    """RAGコンテキスト"""
    rag_sources: List[RAGSource]


class FileAttachment(BaseModel):
    """ファイル添付"""
    type: Literal['image', 'pdf', 'document', 'audio', 'video']
    url: str
    thumbnail: Optional[str] = None
    name: Optional[str] = None
    size: Optional[int] = None


class AgentInfo(BaseModel):
    """エージェント情報"""
    mode: ChatMode
    execution_time_ms: int
    tokens_used: Optional[int] = None


class ChatMessage(BaseModel):
    """チャットメッセージ"""
    # 識別子
    message_id: str
    user_id: str
    room_id: str
    
    # タイムスタンプ
    timestamp: DateTime
    
    # メッセージ情報
    role: MessageRole
    content: str
    
    # RAGコンテキスト（非表示）
    context: Optional[RAGContext] = None
    
    # 添付ファイル
    attachments: Optional[List[FileAttachment]] = None
    
    # エージェント実行情報（assistantロールの場合）
    agent_info: Optional[AgentInfo] = None


class GetChatsParams(BaseModel):
    """チャット一覧取得パラメータ"""
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    sort: Optional[Literal['created_at', 'updated_at']] = 'updated_at'
    order: Optional[Literal['asc', 'desc']] = 'desc'


class GetChatsResponse(BaseModel):
    """チャット一覧レスポンス"""
    chats: List[ChatRoom]
    total: int
    page: int
    limit: int
    total_pages: int


class CreateChatRequest(BaseModel):
    """チャット作成リクエスト"""
    chat_id: Optional[UUID] = None
    message: str
    active_modes: Optional[List[ChatMode]] = None


class CreateChatResponse(BaseModel):
    """チャット作成レスポンス"""
    chat_id: UUID
    message_id: UUID
    title: Optional[str] = None
    created_at: DateTime


class StreamMessage(BaseModel):
    """ストリーミング用の簡略版メッセージ"""
    role: MessageRole
    content: str
    timestamp: Optional[DateTime] = None


class ChatStreamRequest(BaseModel):
    """チャットストリーミングリクエスト"""
    messages: List[StreamMessage]
    chat_id: Optional[str] = None
    modes: Optional[List[ChatMode]] = None
    stream: Literal[True] = True
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    search_keywords: Optional[List[str]] = None


# ============================================
# SSE（Server-Sent Events）型定義
# ドキュメント: /makoto/docs/仕様書/型定義/SSE API型定義.md
# ============================================

class TextChunkEvent(BaseModel):
    """テキストチャンクイベント"""
    type: Literal['text'] = 'text'
    content: str


class ImageGeneratingEvent(BaseModel):
    """画像生成開始イベント"""
    type: Literal['generating_image'] = 'generating_image'
    generating_image: Literal[True] = True


class GeneratedImage(BaseModel):
    """生成された画像"""
    url: str
    prompt: str


class ImageGeneratedEvent(BaseModel):
    """画像生成完了イベント"""
    type: Literal['images'] = 'images'
    images: List[GeneratedImage]


class StreamErrorEvent(BaseModel):
    """ストリームエラーイベント"""
    type: Literal['error'] = 'error'
    error: str


class StreamCompleteEvent(BaseModel):
    """ストリーム完了イベント"""
    type: Literal['done'] = 'done'
    done: Literal[True] = True
    chat_id: str
    message_id: str


# ============================================
# エージェントAPI型定義
# ドキュメント: /makoto/docs/仕様書/型定義/エージェントAPI型定義.md
# ============================================

class AgentStatusContent(BaseModel):
    """エージェントステータス内容"""
    execution_id: str
    agent_type: str
    status: str
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    message: Optional[str] = None


class AgentStatusMessage(BaseModel):
    """エージェントステータスメッセージ"""
    type: Literal['agent_status'] = 'agent_status'
    content: AgentStatusContent


class ModeAnalysis(BaseModel):
    """モード分析"""
    type: str
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    search_keywords: Optional[List[str]] = None


class AnalyzeContext(BaseModel):
    """分析コンテキスト"""
    type: str
    content: str
    metadata: Optional[Dict[str, str]] = None


class AnalyzeRequest(BaseModel):
    """分析リクエスト"""
    prompt: str
    context: Optional[List[AnalyzeContext]] = []


class AnalyzeResponse(BaseModel):
    """分析レスポンス"""
    modes: List[ModeAnalysis]
    analysis: str
    primary_mode: Optional[str] = None


# エージェント思考状態
AgentThinkingStatus = Literal['thinking', 'analyzing', 'searching', 'crawling', 'generating', 'complete']


# ============================================
# ユーティリティ関数
# ============================================

def get_current_datetime() -> DateTime:
    """現在のISO 8601形式の日時を取得"""
    return datetime.now().isoformat()


def generate_uuid() -> UUID:
    """UUID生成"""
    import uuid
    return str(uuid.uuid4())


# ============================================
# ライブラリ管理API型定義
# ドキュメント: /makoto/docs/仕様書/型定義/ライブラリ管理API型定義.md
# ============================================

LibraryStatus = Literal['active', 'processing', 'archived']
VisibilityType = Literal['private', 'team', 'public']


class LibraryVisibility(BaseModel):
    """ライブラリ公開範囲"""
    type: VisibilityType
    allowed_users: Optional[List[str]] = None
    allowed_teams: Optional[List[str]] = None


class Library(BaseModel):
    """ライブラリ"""
    library_id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID
    created_at: DateTime
    updated_at: DateTime
    file_count: int
    total_size: int
    vectorized_count: int
    visibility: LibraryVisibility
    status: LibraryStatus
    last_vectorized_at: Optional[DateTime] = None


class GetLibrariesParams(BaseModel):
    """ライブラリ一覧取得パラメータ"""
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    sort: Optional[Literal['created_at', 'updated_at', 'name']] = 'updated_at'
    order: Optional[Literal['asc', 'desc']] = 'desc'
    filter: Optional[Dict[str, Union[LibraryStatus, VisibilityType]]] = None


class GetLibrariesResponse(BaseModel):
    """ライブラリ一覧レスポンス"""
    libraries: List[Library]
    total: int
    page: int
    limit: int
    total_pages: int


# ============================================
# タスク管理API型定義
# ドキュメント: /makoto/docs/仕様書/型定義/タスク管理API型定義.md
# ============================================

TaskCategory = Literal[
    'text_generation', 'image_generation', 'data_analysis',
    'summarization', 'translation', 'code_generation',
    'creative_writing', 'business', 'other'
]

ExecutionMode = Literal['chat', 'image', 'agent', 'hybrid']
TaskStatus = Literal['draft', 'active', 'deprecated', 'archived']
TaskExecutionStatus = Literal['pending', 'running', 'completed', 'failed', 'cancelled', 'timeout']


class ModelSettings(BaseModel):
    """モデル設定"""
    model: Optional[str] = None
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    image_size: Optional[Literal['1024x1024', '1792x1024', '1024x1792']] = None
    image_quality: Optional[Literal['standard', 'hd']] = None
    image_style: Optional[Literal['vivid', 'natural']] = None
    image_count: Optional[int] = Field(default=1, ge=1, le=10)
    timeout: Optional[int] = None
    retry_count: Optional[int] = None


class ParameterValidation(BaseModel):
    """パラメータバリデーション"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    options: Optional[List[Dict[str, str]]] = None
    allowed_types: Optional[List[str]] = None
    max_size: Optional[int] = None


class TaskParameter(BaseModel):
    """タスクパラメータ"""
    parameter_id: str
    name: str
    label: str
    description: Optional[str] = None
    type: Literal['text', 'number', 'select', 'date', 'boolean', 'file', 'json']
    required: bool
    default_value: Optional[Union[str, int, float, bool, List[str], Dict[str, str]]] = None
    validation: Optional[Union[Dict[str, Union[str, int, float, bool, List[str]]], ParameterValidation]] = None
    ui_type: str
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    display_order: int


class TaskVisibility(BaseModel):
    """タスク公開範囲"""
    type: Literal['private', 'team', 'public', 'tenant', 'specific']
    allowed_users: Optional[List[str]] = None
    allowed_teams: Optional[List[str]] = None
    departments: Optional[List[str]] = None
    roles: Optional[List[str]] = None


class Task(BaseModel):
    """タスク"""
    task_id: str
    name: str
    description: Optional[str] = None
    category: TaskCategory
    tags: List[str]
    icon: Optional[str] = None
    prompt_template: str
    system_prompt: Optional[str] = None
    execution_mode: ExecutionMode
    model_settings: Optional[ModelSettings] = None
    parameters: List[TaskParameter]
    created_by: str
    created_at: str
    updated_at: str
    version: int
    is_latest: bool
    previous_version_id: Optional[str] = None
    visibility: TaskVisibility
    status: TaskStatus
    execution_count: int
    last_executed_at: Optional[str] = None
    average_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)


class ExecutionResult(BaseModel):
    """実行結果"""
    type: Literal['text', 'image', 'mixed']
    text: Optional[str] = None
    images: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ExecutionError(BaseModel):
    """実行エラー"""
    code: str
    message: str
    details: Optional[Any] = None
    occurred_at: str


class TaskExecution(BaseModel):
    """タスク実行履歴"""
    execution_id: str
    task_id: str
    task_version: int
    executed_by: str
    executed_at: str
    parameters: Dict[str, Any]
    status: TaskExecutionStatus
    result: Optional[ExecutionResult] = None
    error: Optional[ExecutionError] = None
    execution_time_ms: int
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None


class GetTasksParams(BaseModel):
    """タスク一覧取得パラメータ"""
    page: Optional[int] = Field(default=1, ge=1)
    limit: Optional[int] = Field(default=20, ge=1, le=100)
    category: Optional[TaskCategory] = None
    status: Optional[TaskStatus] = None
    execution_mode: Optional[ExecutionMode] = None
    created_by: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    sort: Optional[str] = 'updated_at'
    order: Optional[Literal['asc', 'desc']] = 'desc'
    visibility_type: Optional[Literal['private', 'shared', 'all']] = None


class GetTasksResponse(BaseModel):
    """タスク一覧レスポンス"""
    tasks: List[Task]
    total: int
    page: int
    limit: int
    total_pages: int


class CreateTaskRequest(BaseModel):
    """タスク作成リクエスト"""
    name: str
    description: Optional[str] = None
    category: TaskCategory
    tags: Optional[List[str]] = None
    icon: Optional[str] = None
    prompt_template: str
    system_prompt: Optional[str] = None
    execution_mode: ExecutionMode
    model_settings: Optional[ModelSettings] = None
    parameters: List[TaskParameter]
    visibility: TaskVisibility
    status: Optional[TaskStatus] = 'draft'


class UpdateTaskRequest(BaseModel):
    """タスク更新リクエスト"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[TaskCategory] = None
    tags: Optional[List[str]] = None
    icon: Optional[str] = None
    prompt_template: Optional[str] = None
    system_prompt: Optional[str] = None
    execution_mode: Optional[ExecutionMode] = None
    model_settings: Optional[ModelSettings] = None
    parameters: Optional[List[TaskParameter]] = None
    visibility: Optional[TaskVisibility] = None
    status: Optional[TaskStatus] = None
    create_new_version: Optional[bool] = True
    version_notes: Optional[str] = None


class ExecuteTaskRequest(BaseModel):
    """タスク実行リクエスト"""
    parameters: Dict[str, Any]
    options: Optional[Dict[str, Any]] = None


class ExecuteTaskResponse(BaseModel):
    """タスク実行レスポンス"""
    execution_id: str
    status: TaskExecutionStatus
    result: Optional[ExecutionResult] = None
    metadata: Optional[Dict[str, Any]] = None
    stream_url: Optional[str] = None


class UpdateVisibilityRequest(BaseModel):
    """公開範囲更新リクエスト"""
    visibility: TaskVisibility
    notify_users: Optional[bool] = False
    notification_message: Optional[str] = None


# ============================================
# 画像生成API型定義
# ドキュメント: /makoto/docs/仕様書/型定義/画像生成API型定義.md
# ============================================

ImageSize = Literal['1024x1024', '1792x1024', '1024x1792']
ImageQuality = Literal['standard', 'hd']
ImageStyle = Literal['vivid', 'natural']
ImageGenerationStatus = Literal['pending', 'processing', 'completed', 'failed', 'cancelled']


class ImageGenerationRequest(BaseModel):
    """画像生成リクエスト"""
    prompt: str = Field(max_length=4000)
    negative_prompt: Optional[str] = None
    size: Optional[ImageSize] = '1024x1024'
    quality: Optional[ImageQuality] = 'standard'
    style: Optional[ImageStyle] = 'vivid'
    n: Optional[int] = Field(default=1, ge=1, le=10)
    chat_id: Optional[str] = None
    user_tags: Optional[List[str]] = None
    description: Optional[str] = None
    async_: Optional[bool] = Field(default=False, alias='async')
    webhook_url: Optional[str] = None


class ImageMetadata(BaseModel):
    """画像メタデータ"""
    width: int
    height: int
    format: str
    size_bytes: int


class GeneratedImageData(BaseModel):
    """生成された画像データ"""
    image_id: str
    url: str
    thumbnail_url: Optional[str] = None
    revised_prompt: str
    metadata: ImageMetadata


class ImageGenerationCost(BaseModel):
    """画像生成コスト"""
    credits_used: float
    price_usd: float


class ImageGenerationResponse(BaseModel):
    """画像生成レスポンス"""
    images: Optional[List[GeneratedImageData]] = None
    job_id: Optional[str] = None
    status: Optional[ImageGenerationStatus] = None
    request_id: str
    created_at: str
    cost: Optional[ImageGenerationCost] = None


# ============================================
# WebクロールAPI型定義
# ドキュメント: /makoto/docs/仕様書/型定義/WebクロールAPI型定義.md
# ============================================

CrawlJobType = Literal[
    'single_page', 'site_crawl', 'search_based',
    'api_crawl', 'scheduled', 'continuous'
]

CrawlJobStatus = Literal[
    'draft', 'ready', 'running', 'paused',
    'completed', 'failed', 'cancelled'
]


class CrawlResult(BaseModel):
    """クロール結果"""
    url: str
    title: str
    content: str
    images: Optional[List[str]] = None
    links: Optional[List[str]] = None


class WebCrawlRequest(BaseModel):
    """Webクロールリクエスト"""
    url: str
    max_depth: Optional[int] = 1
    max_pages: Optional[int] = 10
    wait_time: Optional[int] = 1
    extract_images: Optional[bool] = False
    extract_links: Optional[bool] = False


class WebCrawlResponse(BaseModel):
    """Webクロールレスポンス"""
    job_id: str
    status: CrawlJobStatus
    results: Optional[List[CrawlResult]] = None
    error: Optional[str] = None