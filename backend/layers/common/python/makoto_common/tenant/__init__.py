"""
マルチテナントモジュール
テナント管理とアイソレーションを提供
"""

from .context import (
    TenantContext,
    get_current_tenant,
    set_current_tenant,
    clear_tenant_context
)

from .manager import (
    TenantManager,
    TenantConfig,
    TenantInfo,
    TenantStatus
)

from .isolation import (
    TenantIsolation,
    ResourceOwnership,
    ResourceType,
    validate_tenant_access,
    enforce_tenant_isolation
)

__all__ = [
    # コンテキスト
    'TenantContext',
    'get_current_tenant',
    'set_current_tenant',
    'clear_tenant_context',
    
    # マネージャー
    'TenantManager',
    'TenantConfig',
    'TenantInfo',
    'TenantStatus',
    
    # アイソレーション
    'TenantIsolation',
    'ResourceOwnership',
    'ResourceType',
    'validate_tenant_access',
    'enforce_tenant_isolation'
]