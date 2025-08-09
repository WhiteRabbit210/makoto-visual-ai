"""
エンティティ型定義
ドメインエンティティの型定義を提供
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from .primitives import (
    AgentId,
    ChatId,
    FileId,
    LibraryId,
    MessageId,
    Metadata,
    ResourceId,
    Tags,
    TenantId,
    UserId
)


# チャットモード型
ChatMode = Literal["chat", "image", "web", "rag"]

# チャット設定型
@dataclass
class ChatSettings:
    """チャット設定"""
    system_prompt: Optional[str] = None  # カスタムシステムプロンプト
    temperature: Optional[float] = None  # 生成温度 (0.0-1.0)
    active_modes: List[ChatMode] = field(default_factory=list)  # 有効なモード
    max_tokens: Optional[int] = None  # 最大トークン数

# ユーザープロファイル型
@dataclass
class UserProfile:
    """ユーザープロファイル情報"""
    display_name: Optional[str] = None  # 表示名
    bio: Optional[str] = None  # 自己紹介
    avatar_url: Optional[str] = None  # アバターURL
    phone_number: Optional[str] = None  # 電話番号
    timezone: Optional[str] = None  # タイムゾーン
    language: str = "ja"  # 言語設定
    country: Optional[str] = None  # 国

# ユーザー設定型
@dataclass
class UserSettings:
    """ユーザー設定"""
    theme: str = "light"  # テーマ (light, dark, auto)
    notifications_enabled: bool = True  # 通知有効フラグ
    email_notifications: bool = True  # メール通知
    auto_save: bool = True  # 自動保存
    default_model: str = "gpt-4"  # デフォルトモデル
    interface_language: str = "ja"  # インターフェース言語

# フィードバック型
@dataclass
class MessageFeedback:
    """メッセージフィードバック"""
    rating: Optional[int] = None  # 評価 (1-5)
    is_helpful: Optional[bool] = None  # 役立ったか
    comment: Optional[str] = None  # コメント
    reported_at: Optional[datetime] = None  # 報告日時
    report_reason: Optional[str] = None  # 報告理由

# ファイル分析結果型
@dataclass
class FileAnalysisResult:
    """ファイル分析結果"""
    content_type: str  # コンテンツタイプ
    language: Optional[str] = None  # 言語（テキストファイルの場合）
    encoding: Optional[str] = None  # エンコーディング
    word_count: Optional[int] = None  # 単語数
    page_count: Optional[int] = None  # ページ数（PDFの場合）
    dimensions: Optional[Dict[str, int]] = None  # 画像/動画の寸法 (width, height)
    duration: Optional[float] = None  # 動画/音声の長さ（秒）
    metadata: Dict[str, str] = field(default_factory=dict)  # その他メタデータ

# エージェント設定型
@dataclass
class AgentConfiguration:
    """エージェント設定"""
    model: str = "gpt-4"  # 使用モデル
    temperature: float = 0.7  # 生成温度
    max_tokens: Optional[int] = None  # 最大トークン数
    system_prompt: Optional[str] = None  # システムプロンプト
    response_format: Optional[str] = None  # レスポンス形式
    stop_sequences: List[str] = field(default_factory=list)  # 停止シーケンス
    top_p: Optional[float] = None  # Top-p サンプリング
    frequency_penalty: Optional[float] = None  # 頻度ペナルティ
    presence_penalty: Optional[float] = None  # 存在ペナルティ

# インデックスメタデータ型
@dataclass
class IndexMetadata:
    """インデックスメタデータ"""
    vector_db_type: Optional[str] = None  # ベクトルDBタイプ (pinecone, weaviate, etc.)
    index_name: Optional[str] = None  # インデックス名
    embedding_model: Optional[str] = None  # 埋め込みモデル
    dimension: Optional[int] = None  # ベクトル次元数
    total_vectors: int = 0  # 総ベクトル数
    last_indexed_at: Optional[datetime] = None  # 最終インデックス日時
    index_version: Optional[str] = None  # インデックスバージョン


@dataclass
class BaseEntity:
    """
    基底エンティティ
    すべてのエンティティの基底クラス
    """
    id: ResourceId  # エンティティID
    tenant_id: TenantId  # テナントID
    created_at: datetime  # 作成日時
    updated_at: datetime  # 更新日時
    created_by: UserId  # 作成者
    updated_by: UserId  # 更新者
    version: int = 1  # バージョン番号
    is_deleted: bool = False  # 削除フラグ
    metadata: Metadata = field(default_factory=dict)  # メタデータ


@dataclass
class User(BaseEntity):
    """
    ユーザーエンティティ
    """
    username: str  # ユーザー名（ログインID、必須）
    email: Optional[str] = None  # メールアドレス（オプション）
    email_verified: bool = False  # メール確認状態
    cognito_sub: Optional[str] = None  # Cognitoユーザーサブ
    display_name: Optional[str] = None  # 表示名
    account_type: str = "standard"  # アカウントタイプ (standard, admin, service, guest)
    roles: List[str] = field(default_factory=list)  # ロールリスト
    status: str = "active"  # ステータス (active, inactive, suspended)
    profile: Optional[UserProfile] = None  # プロファイル情報
    settings: Optional[UserSettings] = None  # 設定情報
    organization_id: Optional[str] = None  # 所属組織ID
    last_login_at: Optional[datetime] = None  # 最終ログイン日時
    login_count: int = 0  # ログイン回数


@dataclass
class Chat(BaseEntity):
    """
    チャットエンティティ
    """
    id: ChatId  # チャットID (BaseEntityのidをオーバーライド)
    user_id: UserId  # 所有者ID
    title: str  # タイトル
    model: str = "gpt-4"  # 使用モデル
    status: str = "active"  # ステータス (active, archived, deleted)
    message_count: int = 0  # メッセージ数
    last_message: Optional[Dict[str, str]] = None  # 最後のメッセージ (text, timestamp, role)
    last_message_at: Optional[datetime] = None  # 最終メッセージ日時
    settings: Optional[ChatSettings] = None  # チャット設定


@dataclass
class Message(BaseEntity):
    """
    メッセージエンティティ
    """
    id: MessageId  # メッセージID
    chat_id: ChatId  # チャットID
    role: str  # ロール (user, assistant, system)
    content: str  # メッセージ内容
    model: Optional[str] = None  # 使用モデル (assistantの場合)
    attachments: List[FileId] = field(default_factory=list)  # 添付ファイル
    references: List[MessageId] = field(default_factory=list)  # 参照メッセージ
    tokens: Optional[Dict[str, int]] = None  # トークン数 (prompt_tokens, completion_tokens, total_tokens)
    feedback: Optional[MessageFeedback] = None  # フィードバック
    is_edited: bool = False  # 編集済みフラグ
    edited_at: Optional[datetime] = None  # 編集日時


@dataclass
class File(BaseEntity):
    """
    ファイルエンティティ
    """
    id: FileId  # ファイルID
    filename: str  # ファイル名
    content_type: str  # コンテンツタイプ
    size: int  # ファイルサイズ (バイト)
    storage_path: str  # ストレージパス
    url: Optional[str] = None  # アクセスURL
    thumbnail_url: Optional[str] = None  # サムネイルURL
    checksum: Optional[str] = None  # チェックサム
    upload_status: str = "pending"  # アップロード状態
    processing_status: Optional[str] = None  # 処理状態
    extracted_text: Optional[str] = None  # 抽出テキスト
    analysis_result: Optional[FileAnalysisResult] = None  # ファイル分析結果


@dataclass
class Agent(BaseEntity):
    """
    エージェントエンティティ
    """
    id: AgentId  # エージェントID
    name: str  # エージェント名
    description: str  # 説明
    type: str  # タイプ (chat, task, workflow)
    configuration: Optional[AgentConfiguration] = None  # エージェント設定
    capabilities: List[str] = field(default_factory=list)  # 機能リスト
    model: str = "gpt-4"  # デフォルトモデル
    prompt_template: Optional[str] = None  # プロンプトテンプレート
    tools: List[str] = field(default_factory=list)  # 利用可能ツール名リスト
    status: str = "active"  # ステータス
    usage_count: int = 0  # 使用回数
    last_used_at: Optional[datetime] = None  # 最終使用日時


@dataclass
class Library(BaseEntity):
    """
    ライブラリエンティティ
    """
    id: LibraryId  # ライブラリID
    name: str  # ライブラリ名
    description: Optional[str] = None  # 説明
    type: str  # タイプ (document, image, audio, video)
    files: List[FileId] = field(default_factory=list)  # ファイルリスト
    index_status: str = "pending"  # インデックス状態
    index_metadata: Optional[IndexMetadata] = None  # インデックスメタデータ
    access_level: str = "private"  # アクセスレベル (private, shared, public)
    shared_with: List[UserId] = field(default_factory=list)  # 共有ユーザーID（マルチテナント環境では同一テナント内のみ）
    tags: Tags = field(default_factory=list)  # タグ
    total_size: int = 0  # 総サイズ (バイト)
    file_count: int = 0  # ファイル数