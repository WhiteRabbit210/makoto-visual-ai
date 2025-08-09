"""
テナント管理
テナントのライフサイクル管理とマルチクラウド対応
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..types.primitives import TenantId, UserId
from ..utils import get_logger, get_uuid

logger = get_logger(__name__)


class TenantStatus(Enum):
    """テナントステータス"""
    PROVISIONING = "provisioning"  # プロビジョニング中
    ACTIVE = "active"  # アクティブ
    SUSPENDED = "suspended"  # 一時停止
    INACTIVE = "inactive"  # 非アクティブ
    DELETED = "deleted"  # 削除済み


class TenantPlan(Enum):
    """テナントプラン"""
    FREE = "free"  # 無料プラン
    STARTER = "starter"  # スタータープラン
    PROFESSIONAL = "professional"  # プロフェッショナルプラン
    ENTERPRISE = "enterprise"  # エンタープライズプラン


class CloudProvider(Enum):
    """クラウドプロバイダー"""
    AWS = "aws"  # Amazon Web Services
    AZURE = "azure"  # Microsoft Azure
    CUSTOM = "custom"  # カスタム環境


class LLMProvider(Enum):
    """LLMプロバイダー"""
    AZURE_OPENAI = "azure_openai"  # Azure OpenAI Service
    OPENAI = "openai"  # OpenAI API
    ANTHROPIC = "anthropic"  # Claude API
    AWS_BEDROCK = "aws_bedrock"  # Amazon Bedrock
    CUSTOM = "custom"  # カスタムLLM


@dataclass
class LLMConfiguration:
    """
    LLM設定
    テナントが提供するLLMサービスの設定
    """
    provider: LLMProvider  # LLMプロバイダー
    endpoint: Optional[str] = None  # エンドポイントURL（Azure OpenAIの場合）
    api_key_ref: str = ""  # APIキー参照（Secrets Manager）
    api_version: Optional[str] = None  # APIバージョン
    models: Dict[str, str] = field(default_factory=lambda: {
        "chat": "gpt-4",
        "embedding": "text-embedding-ada-002"
    })  # 利用可能モデル
    region: Optional[str] = None  # リージョン
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "rpm": 600,  # requests per minute
        "tpm": 90000  # tokens per minute
    })  # レート制限


@dataclass
class DatabaseConfiguration:
    """
    データベース設定
    テナントのデータベース設定
    """
    # AWS環境
    dynamodb_table_prefix: Optional[str] = None  # DynamoDBテーブル接頭辞
    
    # Azure環境
    cosmosdb_endpoint: Optional[str] = None  # CosmosDBエンドポイント
    cosmosdb_database: Optional[str] = None  # CosmosDBデータベース名
    cosmosdb_key_ref: Optional[str] = None  # CosmosDB接続キー参照
    
    # カスタム環境
    custom_db_type: Optional[str] = None  # PostgreSQL, MongoDB等
    custom_db_connection_ref: Optional[str] = None  # 接続文字列参照


@dataclass
class StorageConfiguration:
    """
    ストレージ設定
    テナントのストレージ設定
    """
    # AWS環境
    s3_bucket: Optional[str] = None  # S3バケット名
    s3_prefix: Optional[str] = None  # S3プレフィックス
    
    # Azure環境
    blob_container: Optional[str] = None  # Blobコンテナ名
    blob_account_name: Optional[str] = None  # ストレージアカウント名
    blob_connection_ref: Optional[str] = None  # 接続文字列参照
    
    # カスタム環境
    custom_storage_type: Optional[str] = None  # MinIO等
    custom_storage_endpoint: Optional[str] = None  # エンドポイント
    custom_storage_credentials_ref: Optional[str] = None  # 認証情報参照


@dataclass
class TenantConfig:
    """
    テナント設定
    マルチクラウド対応のテナント設定
    """
    # 基本情報
    tenant_id: TenantId  # テナントID
    name: str  # テナント名
    organization_name: Optional[str] = None  # 組織名
    
    # プランとステータス
    plan: TenantPlan = TenantPlan.FREE  # プラン
    status: TenantStatus = TenantStatus.ACTIVE  # ステータス
    
    # クラウド環境
    cloud_provider: CloudProvider = CloudProvider.AWS  # クラウドプロバイダー
    cloud_region: str = "ap-northeast-1"  # リージョン
    
    # LLM設定（テナントが提供）
    llm_config: Optional[LLMConfiguration] = None  # LLM設定
    
    # データベース設定
    database_config: Optional[DatabaseConfiguration] = None  # データベース設定
    
    # ストレージ設定
    storage_config: Optional[StorageConfiguration] = None  # ストレージ設定
    
    # リソース制限
    max_storage_gb: int = 10  # 最大ストレージ（GB）
    max_users: int = 5  # 最大ユーザー数
    max_api_calls_per_day: int = 10000  # 1日あたりの最大API呼び出し数
    max_file_size_mb: int = 100  # 最大ファイルサイズ（MB）
    
    # 機能フラグ
    features: Dict[str, bool] = field(default_factory=lambda: {
        "chat": True,
        "image_generation": False,
        "audio_processing": False,
        "web_search": False,
        "rag": False,
        "agents": False,
        "plugins": False
    })
    
    # シークレット管理
    secrets_manager_path: str = ""  # Secrets Managerパス
    
    # カスタムドメイン
    custom_domain: Optional[str] = None  # カスタムドメイン
    
    # メタデータ
    metadata: Dict[str, Any] = field(default_factory=dict)  # その他のメタデータ
    
    def __post_init__(self):
        """初期化後処理"""
        # Secrets Managerパスのデフォルト設定
        if not self.secrets_manager_path:
            self.secrets_manager_path = f"/makoto/{self.tenant_id}/"
        
        # クラウドプロバイダー別のデフォルト設定
        if self.cloud_provider == CloudProvider.AWS:
            self._setup_aws_defaults()
        elif self.cloud_provider == CloudProvider.AZURE:
            self._setup_azure_defaults()
    
    def _setup_aws_defaults(self):
        """AWS環境のデフォルト設定"""
        if not self.database_config:
            self.database_config = DatabaseConfiguration()
        if not self.database_config.dynamodb_table_prefix:
            self.database_config.dynamodb_table_prefix = f"makoto-{self.tenant_id}-"
        
        if not self.storage_config:
            self.storage_config = StorageConfiguration()
        if not self.storage_config.s3_bucket:
            self.storage_config.s3_bucket = f"makoto-{self.tenant_id}-assets"
        if not self.storage_config.s3_prefix:
            self.storage_config.s3_prefix = f"tenants/{self.tenant_id}/"
    
    def _setup_azure_defaults(self):
        """Azure環境のデフォルト設定"""
        if not self.database_config:
            self.database_config = DatabaseConfiguration()
        if not self.database_config.cosmosdb_database:
            self.database_config.cosmosdb_database = f"makoto-{self.tenant_id}"
        
        if not self.storage_config:
            self.storage_config = StorageConfiguration()
        if not self.storage_config.blob_container:
            self.storage_config.blob_container = f"{self.tenant_id}-assets"


@dataclass
class TenantInfo:
    """
    テナント情報
    テナントの詳細情報
    """
    # 基本情報
    tenant_id: TenantId  # テナントID
    name: str  # テナント名
    description: Optional[str] = None  # 説明
    
    # 組織情報
    organization_name: Optional[str] = None  # 組織名
    organization_id: Optional[str] = None  # 組織ID
    contact_email: Optional[str] = None  # 連絡先メール
    contact_phone: Optional[str] = None  # 連絡先電話番号
    
    # 管理者
    owner_id: UserId = None  # オーナーユーザーID
    admin_ids: List[UserId] = field(default_factory=list)  # 管理者ユーザーID
    
    # 統計情報
    user_count: int = 0  # ユーザー数
    storage_used_gb: float = 0.0  # 使用ストレージ（GB）
    api_calls_today: int = 0  # 本日のAPI呼び出し数
    llm_tokens_today: int = 0  # 本日のLLMトークン使用量
    
    # 日時情報
    created_at: datetime = field(default_factory=datetime.utcnow)  # 作成日時
    updated_at: datetime = field(default_factory=datetime.utcnow)  # 更新日時
    last_active_at: Optional[datetime] = None  # 最終アクティブ日時
    
    # 設定
    config: Optional[TenantConfig] = None  # テナント設定


class TenantManager:
    """
    テナントマネージャー
    マルチクラウド対応のテナント管理
    """
    
    def __init__(self):
        """初期化"""
        self.tenants: Dict[TenantId, TenantInfo] = {}  # メモリ内キャッシュ
    
    def create_tenant(
        self,
        name: str,
        owner_id: UserId,
        cloud_provider: CloudProvider = CloudProvider.AWS,
        plan: TenantPlan = TenantPlan.FREE,
        organization_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        llm_provider: Optional[LLMProvider] = None,
        llm_endpoint: Optional[str] = None,
        llm_api_key_ref: Optional[str] = None
    ) -> TenantInfo:
        """
        テナントを作成
        
        Args:
            name: テナント名
            owner_id: オーナーユーザーID
            cloud_provider: クラウドプロバイダー
            plan: プラン
            organization_name: 組織名
            contact_email: 連絡先メール
            llm_provider: LLMプロバイダー
            llm_endpoint: LLMエンドポイント
            llm_api_key_ref: LLM APIキー参照
            
        Returns:
            作成されたテナント情報
        """
        # テナントID生成
        tenant_id = TenantId(f"tenant-{get_uuid()[:8]}")
        
        # テナント設定作成
        config = TenantConfig(
            tenant_id=tenant_id,
            name=name,
            organization_name=organization_name,
            cloud_provider=cloud_provider,
            plan=plan,
            status=TenantStatus.PROVISIONING
        )
        
        # LLM設定（テナント提供）
        if llm_provider:
            config.llm_config = LLMConfiguration(
                provider=llm_provider,
                endpoint=llm_endpoint,
                api_key_ref=llm_api_key_ref or f"{config.secrets_manager_path}llm-key"
            )
        
        # プランに応じた設定
        self._configure_by_plan(config, plan)
        
        # テナント情報作成
        tenant_info = TenantInfo(
            tenant_id=tenant_id,
            name=name,
            organization_name=organization_name,
            contact_email=contact_email,
            owner_id=owner_id,
            admin_ids=[owner_id],
            config=config
        )
        
        # キャッシュに保存
        self.tenants[tenant_id] = tenant_info
        
        logger.info(f"テナント作成: {tenant_id} ({name}) - クラウド: {cloud_provider.value}")
        
        # プロビジョニング後にアクティブ化
        config.status = TenantStatus.ACTIVE
        
        return tenant_info
    
    def _configure_by_plan(self, config: TenantConfig, plan: TenantPlan):
        """プランに応じた設定"""
        if plan == TenantPlan.STARTER:
            config.max_storage_gb = 50
            config.max_users = 20
            config.max_api_calls_per_day = 50000
            config.features["image_generation"] = True
            config.features["web_search"] = True
        elif plan == TenantPlan.PROFESSIONAL:
            config.max_storage_gb = 200
            config.max_users = 100
            config.max_api_calls_per_day = 200000
            config.features["image_generation"] = True
            config.features["audio_processing"] = True
            config.features["web_search"] = True
            config.features["rag"] = True
            config.features["agents"] = True
        elif plan == TenantPlan.ENTERPRISE:
            config.max_storage_gb = 1000
            config.max_users = -1  # 無制限
            config.max_api_calls_per_day = -1  # 無制限
            config.features = {key: True for key in config.features}  # 全機能有効
    
    def get_tenant(self, tenant_id: TenantId) -> Optional[TenantInfo]:
        """
        テナント情報を取得
        
        Args:
            tenant_id: テナントID
            
        Returns:
            テナント情報（存在しない場合None）
        """
        return self.tenants.get(tenant_id)
    
    def update_tenant_llm(
        self,
        tenant_id: TenantId,
        llm_provider: LLMProvider,
        endpoint: Optional[str] = None,
        api_key_ref: Optional[str] = None,
        models: Optional[Dict[str, str]] = None
    ) -> Optional[TenantInfo]:
        """
        テナントのLLM設定を更新
        
        Args:
            tenant_id: テナントID
            llm_provider: LLMプロバイダー
            endpoint: エンドポイント
            api_key_ref: APIキー参照
            models: 利用可能モデル
            
        Returns:
            更新されたテナント情報
        """
        tenant_info = self.get_tenant(tenant_id)
        if not tenant_info or not tenant_info.config:
            return None
        
        # LLM設定更新
        if not tenant_info.config.llm_config:
            tenant_info.config.llm_config = LLMConfiguration(provider=llm_provider)
        else:
            tenant_info.config.llm_config.provider = llm_provider
        
        if endpoint:
            tenant_info.config.llm_config.endpoint = endpoint
        if api_key_ref:
            tenant_info.config.llm_config.api_key_ref = api_key_ref
        if models:
            tenant_info.config.llm_config.models = models
        
        tenant_info.updated_at = datetime.utcnow()
        
        logger.info(f"テナントLLM設定更新: {tenant_id} - プロバイダー: {llm_provider.value}")
        
        return tenant_info
    
    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        plan: Optional[TenantPlan] = None,
        cloud_provider: Optional[CloudProvider] = None
    ) -> List[TenantInfo]:
        """
        テナント一覧を取得
        
        Args:
            status: フィルタするステータス
            plan: フィルタするプラン
            cloud_provider: フィルタするクラウドプロバイダー
            
        Returns:
            テナント情報リスト
        """
        tenants = list(self.tenants.values())
        
        # フィルタリング
        if status:
            tenants = [
                t for t in tenants
                if t.config and t.config.status == status
            ]
        
        if plan:
            tenants = [
                t for t in tenants
                if t.config and t.config.plan == plan
            ]
        
        if cloud_provider:
            tenants = [
                t for t in tenants
                if t.config and t.config.cloud_provider == cloud_provider
            ]
        
        return tenants