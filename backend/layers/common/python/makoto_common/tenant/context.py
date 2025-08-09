"""
テナントコンテキスト管理
現在のテナント情報を管理
"""

import contextvars
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from ..types.primitives import TenantId, UserId


@dataclass
class TenantContext:
    """
    テナントコンテキスト
    リクエスト単位でテナント情報を保持
    """
    tenant_id: TenantId  # テナントID
    user_id: UserId  # ユーザーID
    request_id: str  # リクエストID
    created_at: datetime  # コンテキスト作成時刻
    
    # テナント設定
    config: Optional[Dict[str, Any]] = None  # テナント固有設定
    
    # リソース制限
    max_storage_gb: Optional[int] = None  # 最大ストレージ容量（GB）
    max_users: Optional[int] = None  # 最大ユーザー数
    max_api_calls_per_day: Optional[int] = None  # 1日あたりの最大API呼び出し数
    
    # 機能フラグ
    features: Optional[Dict[str, bool]] = None  # 有効な機能
    
    # メタデータ
    metadata: Optional[Dict[str, Any]] = None  # その他のメタデータ
    
    def has_feature(self, feature_name: str) -> bool:
        """
        機能が有効かチェック
        
        Args:
            feature_name: 機能名
            
        Returns:
            有効な場合True
        """
        if not self.features:
            return False
        return self.features.get(feature_name, False)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            設定値
        """
        if not self.config:
            return default
        return self.config.get(key, default)


# コンテキスト変数（スレッドローカルのような動作）
_tenant_context: contextvars.ContextVar[Optional[TenantContext]] = contextvars.ContextVar(
    'tenant_context',
    default=None
)


def get_current_tenant() -> Optional[TenantContext]:
    """
    現在のテナントコンテキストを取得
    
    Returns:
        テナントコンテキスト（設定されていない場合None）
    """
    return _tenant_context.get()


def set_current_tenant(context: TenantContext) -> contextvars.Token:
    """
    テナントコンテキストを設定
    
    Args:
        context: テナントコンテキスト
        
    Returns:
        コンテキストトークン（復元用）
    """
    return _tenant_context.set(context)


def clear_tenant_context() -> None:
    """
    テナントコンテキストをクリア
    """
    _tenant_context.set(None)


def require_tenant_context() -> TenantContext:
    """
    テナントコンテキストを要求（必須）
    
    Returns:
        テナントコンテキスト
        
    Raises:
        RuntimeError: テナントコンテキストが設定されていない場合
    """
    context = get_current_tenant()
    if not context:
        raise RuntimeError("テナントコンテキストが設定されていません")
    return context


class TenantContextManager:
    """
    テナントコンテキストマネージャー
    with文で使用
    """
    
    def __init__(self, context: TenantContext):
        """
        初期化
        
        Args:
            context: テナントコンテキスト
        """
        self.context = context
        self.token: Optional[contextvars.Token] = None
    
    def __enter__(self) -> TenantContext:
        """
        コンテキスト開始
        
        Returns:
            テナントコンテキスト
        """
        self.token = set_current_tenant(self.context)
        return self.context
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        コンテキスト終了
        """
        if self.token:
            _tenant_context.reset(self.token)


def with_tenant_context(context: TenantContext) -> TenantContextManager:
    """
    テナントコンテキストを一時的に設定
    
    Args:
        context: テナントコンテキスト
        
    Returns:
        コンテキストマネージャー
        
    Example:
        ```python
        with with_tenant_context(context):
            # この中ではcontextが有効
            process_tenant_data()
        ```
    """
    return TenantContextManager(context)