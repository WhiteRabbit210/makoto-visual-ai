"""
MAKOTO 共通ライブラリ
Lambda Layer用共通ライブラリ

Copyright (c) 2025 MAKOTO Visual AI
"""

__version__ = "1.0.0"
__author__ = "MAKOTO Team"

# バージョン情報
VERSION_INFO = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'release': 'stable',
    'build': '20250807'
}

# 基本的なインポート
from .utils import (
    get_logger,
    get_uuid,
    get_timestamp,
    format_datetime,
    parse_datetime,
    calculate_hash,
    retry_with_backoff,
    chunk_list,
    merge_dicts,
    sanitize_string,
    validate_email,
    validate_phone,
    format_error_response,
    format_success_response
)

# エラークラス
from .errors import (
    MakotoError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError
)

# 型定義
from .types import (
    TenantId,
    UserId,
    ResourceId,
    Timestamp
)

__all__ = [
    # バージョン
    '__version__',
    'VERSION_INFO',
    
    # ユーティリティ
    'get_logger',
    'get_uuid',
    'get_timestamp',
    'format_datetime',
    'parse_datetime',
    'calculate_hash',
    'retry_with_backoff',
    'chunk_list',
    'merge_dicts',
    'sanitize_string',
    'validate_email',
    'validate_phone',
    'format_error_response',
    'format_success_response',
    
    # エラー
    'MakotoError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'NotFoundError',
    'ConflictError',
    'RateLimitError',
    'ServiceUnavailableError',
    
    # 型
    'TenantId',
    'UserId',
    'ResourceId',
    'Timestamp'
]