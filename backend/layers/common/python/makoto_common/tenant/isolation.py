"""
テナントアイソレーション
テナント間の完全なデータ分離を実装
"""

from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from ..types.primitives import TenantId, UserId, ResourceId
from ..utils import get_logger
from .context import get_current_tenant, require_tenant_context

logger = get_logger(__name__)


class ResourceType(Enum):
    """リソースタイプ"""
    USER = "user"  # ユーザー
    CHAT = "chat"  # チャット
    MESSAGE = "message"  # メッセージ
    FILE = "file"  # ファイル
    DOCUMENT = "document"  # ドキュメント
    KNOWLEDGE = "knowledge"  # ナレッジベース
    PROMPT = "prompt"  # プロンプトテンプレート
    MODEL_CONFIG = "model_config"  # モデル設定
    AGENT = "agent"  # エージェント
    PLUGIN = "plugin"  # プラグイン
    API_KEY = "api_key"  # APIキー
    WEBHOOK = "webhook"  # Webhook
    AUDIT_LOG = "audit_log"  # 監査ログ


@dataclass
class ResourceOwnership:
    """
    リソース所有権
    テナントとユーザーによるリソース所有を管理
    """
    resource_id: ResourceId  # リソースID
    resource_type: ResourceType  # リソースタイプ
    tenant_id: TenantId  # 所有テナントID
    owner_id: UserId  # 所有者ユーザーID
    
    # メタデータ
    created_at: Optional[str] = None  # 作成日時
    updated_at: Optional[str] = None  # 更新日時
    metadata: Dict[str, Any] = field(default_factory=dict)  # その他メタデータ
    
    def is_owner(
        self,
        tenant_id: TenantId,
        user_id: UserId
    ) -> bool:
        """
        所有者かチェック
        
        Args:
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            所有者の場合True
        """
        return self.tenant_id == tenant_id and self.owner_id == user_id
    
    def belongs_to_tenant(self, tenant_id: TenantId) -> bool:
        """
        テナントに属するかチェック
        
        Args:
            tenant_id: テナントID
            
        Returns:
            テナントに属する場合True
        """
        return self.tenant_id == tenant_id


class TenantIsolation:
    """
    テナントアイソレーション管理
    テナント間の完全なデータ分離を保証
    """
    
    def __init__(self):
        """初期化"""
        self.resource_registry: Dict[ResourceId, ResourceOwnership] = {}  # リソースレジストリ
    
    def register_resource(
        self,
        resource_id: ResourceId,
        resource_type: ResourceType,
        tenant_id: TenantId,
        owner_id: UserId,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResourceOwnership:
        """
        リソースを登録
        
        Args:
            resource_id: リソースID
            resource_type: リソースタイプ
            tenant_id: テナントID
            owner_id: 所有者ID
            metadata: メタデータ
            
        Returns:
            リソース所有権情報
        """
        from datetime import datetime
        
        ownership = ResourceOwnership(
            resource_id=resource_id,
            resource_type=resource_type,
            tenant_id=tenant_id,
            owner_id=owner_id,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )
        
        self.resource_registry[resource_id] = ownership
        
        logger.info(
            f"リソース登録: {resource_id} "
            f"(タイプ: {resource_type.value}, "
            f"テナント: {tenant_id}, "
            f"所有者: {owner_id})"
        )
        
        return ownership
    
    def verify_ownership(
        self,
        resource_id: ResourceId,
        tenant_id: TenantId,
        user_id: UserId
    ) -> bool:
        """
        リソース所有権を確認
        
        Args:
            resource_id: リソースID
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            所有者の場合True
        """
        ownership = self.resource_registry.get(resource_id)
        if not ownership:
            logger.warning(f"未登録リソース: {resource_id}")
            return False
        
        is_owner = ownership.is_owner(tenant_id, user_id)
        
        if not is_owner:
            logger.warning(
                f"所有権なし: リソース {resource_id} "
                f"(要求テナント: {tenant_id}, 要求ユーザー: {user_id}, "
                f"実際のテナント: {ownership.tenant_id}, 実際の所有者: {ownership.owner_id})"
            )
        
        return is_owner
    
    def verify_tenant_access(
        self,
        resource_id: ResourceId,
        tenant_id: TenantId
    ) -> bool:
        """
        テナントアクセスを確認（読み取り専用）
        
        Args:
            resource_id: リソースID
            tenant_id: テナントID
            
        Returns:
            アクセス可能な場合True
        """
        ownership = self.resource_registry.get(resource_id)
        if not ownership:
            logger.warning(f"未登録リソース: {resource_id}")
            return False
        
        # テナントが一致するかチェック
        has_access = ownership.belongs_to_tenant(tenant_id)
        
        if not has_access:
            logger.warning(
                f"テナントアクセス拒否: リソース {resource_id} "
                f"(要求テナント: {tenant_id}, 実際のテナント: {ownership.tenant_id})"
            )
        
        return has_access
    
    def get_resource_ownership(
        self,
        resource_id: ResourceId
    ) -> Optional[ResourceOwnership]:
        """
        リソース所有権情報を取得
        
        Args:
            resource_id: リソースID
            
        Returns:
            リソース所有権情報（存在しない場合None）
        """
        return self.resource_registry.get(resource_id)
    
    def delete_resource(
        self,
        resource_id: ResourceId,
        tenant_id: TenantId,
        user_id: UserId
    ) -> bool:
        """
        リソースを削除
        
        Args:
            resource_id: リソースID
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            削除成功した場合True
        """
        # 所有権確認
        if not self.verify_ownership(resource_id, tenant_id, user_id):
            return False
        
        # レジストリから削除
        del self.resource_registry[resource_id]
        
        logger.info(
            f"リソース削除: {resource_id} "
            f"(テナント: {tenant_id}, ユーザー: {user_id})"
        )
        
        return True
    
    def get_tenant_resources(
        self,
        tenant_id: TenantId,
        resource_type: Optional[ResourceType] = None
    ) -> List[ResourceOwnership]:
        """
        テナントのリソース一覧を取得
        
        Args:
            tenant_id: テナントID
            resource_type: フィルタするリソースタイプ
            
        Returns:
            リソース所有権リスト
        """
        resources = []
        
        for ownership in self.resource_registry.values():
            # テナントIDチェック
            if ownership.tenant_id != tenant_id:
                continue
            
            # リソースタイプフィルタ
            if resource_type and ownership.resource_type != resource_type:
                continue
            
            resources.append(ownership)
        
        return resources


# グローバルインスタンス
_isolation_manager = TenantIsolation()


def get_isolation_manager() -> TenantIsolation:
    """アイソレーションマネージャーを取得"""
    return _isolation_manager


def validate_tenant_access(
    resource_id: ResourceId,
    read_only: bool = False
) -> bool:
    """
    現在のテナントコンテキストでアクセス可能かチェック
    
    Args:
        resource_id: リソースID
        read_only: 読み取り専用アクセスの場合True
        
    Returns:
        アクセス可能な場合True
    """
    context = get_current_tenant()
    if not context:
        return False
    
    if read_only:
        # 読み取り専用: テナントが一致すればOK
        return _isolation_manager.verify_tenant_access(
            resource_id=resource_id,
            tenant_id=context.tenant_id
        )
    else:
        # 書き込み: 所有者である必要がある
        return _isolation_manager.verify_ownership(
            resource_id=resource_id,
            tenant_id=context.tenant_id,
            user_id=context.user_id
        )


def enforce_tenant_isolation(
    resource_type: ResourceType,
    read_only: bool = False
) -> Callable:
    """
    テナントアイソレーションを強制するデコレーター
    
    Args:
        resource_type: リソースタイプ
        read_only: 読み取り専用の場合True
        
    Returns:
        デコレーター関数
        
    Example:
        ```python
        @enforce_tenant_isolation(ResourceType.CHAT, read_only=True)
        def get_chat(chat_id: str) -> Chat:
            # この関数はテナントコンテキストが必須
            # かつリソースへのアクセス権限がチェックされる
            pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # テナントコンテキスト必須
            context = require_tenant_context()
            
            # リソースIDを引数から取得（第1引数と仮定）
            resource_id = None
            if args:
                resource_id = args[0]
            elif 'resource_id' in kwargs:
                resource_id = kwargs['resource_id']
            elif 'id' in kwargs:
                resource_id = kwargs['id']
            
            # リソースIDがある場合はアクセスチェック
            if resource_id:
                if not validate_tenant_access(resource_id, read_only):
                    raise PermissionError(
                        f"テナント {context.tenant_id} はリソース {resource_id} "
                        f"へのアクセス権限がありません"
                    )
            
            # 関数実行
            return func(*args, **kwargs)
        
        return wrapper
    return decorator