"""
型定義モジュール
共通で使用される型定義を提供
"""

from .primitives import (
    TenantId,
    UserId,
    SessionId,
    ResourceId,
    Timestamp,
    UnixTimestamp,
    Amount,
    Percentage,
    Count
)

from .entities import (
    BaseEntity,
    User,
    UserProfile,
    UserSettings,
    Chat,
    ChatSettings,
    ChatMode,
    Message,
    MessageFeedback,
    File,
    FileAnalysisResult,
    Agent,
    AgentConfiguration,
    Library,
    IndexMetadata
)

from .api import (
    BaseRequest,
    BaseResponse,
    PaginationRequest,
    PaginatedResponse,
    ErrorDetail,
    ErrorResponse
)

__all__ = [
    # 基本型
    'TenantId',
    'UserId',
    'SessionId',
    'ResourceId',
    'Timestamp',
    'UnixTimestamp',
    'Amount',
    'Percentage',
    'Count',
    
    # エンティティ
    'BaseEntity',
    'User',
    'UserProfile',
    'UserSettings',
    'Chat',
    'ChatSettings',
    'ChatMode',
    'Message',
    'MessageFeedback',
    'File',
    'FileAnalysisResult',
    'Agent',
    'AgentConfiguration',
    'Library',
    'IndexMetadata',
    
    # API型
    'BaseRequest',
    'BaseResponse',
    'PaginationRequest',
    'PaginatedResponse',
    'ErrorDetail',
    'ErrorResponse'
]