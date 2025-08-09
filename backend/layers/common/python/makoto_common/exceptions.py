"""
例外処理ユーティリティ
エラーハンドリングと例外管理のユーティリティ
"""

import logging
import sys
import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type, Union
import json
from datetime import datetime

from .errors import (
    MakotoError,
    ErrorCode,
    ErrorSeverity,
    ErrorDetail,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    TenantError,
    DatabaseError,
    LLMError
)

logger = logging.getLogger(__name__)


class ErrorHandler:
    """
    エラーハンドラー
    エラーのログ出力、変換、レポートを管理
    """
    
    def __init__(self, service_name: str = "makoto"):
        """
        初期化
        
        Args:
            service_name: サービス名
        """
        self.service_name = service_name
        self.error_count = {}
        self.last_errors = []
        self.max_last_errors = 100
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        log_level: Optional[int] = None
    ) -> ErrorDetail:
        """
        エラーをハンドリング
        
        Args:
            error: 例外
            context: コンテキスト情報
            log_level: ログレベル
            
        Returns:
            エラー詳細
        """
        # MakotoErrorの場合
        if isinstance(error, MakotoError):
            error_detail = error.error_detail
            if context:
                error_detail.context.update(context)
        else:
            # 一般的な例外の場合
            error_detail = self._convert_to_error_detail(error, context)
        
        # ログレベルの決定
        if log_level is None:
            log_level = self._get_log_level(error_detail.severity)
        
        # ログ出力
        self._log_error(error_detail, log_level)
        
        # 統計情報を更新
        self._update_statistics(error_detail)
        
        return error_detail
    
    def _convert_to_error_detail(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorDetail:
        """
        一般的な例外をErrorDetailに変換
        """
        # エラータイプによる分類
        if isinstance(error, ValueError):
            code = ErrorCode.VALIDATION_ERROR
            severity = ErrorSeverity.LOW
        elif isinstance(error, PermissionError):
            code = ErrorCode.FORBIDDEN
            severity = ErrorSeverity.MEDIUM
        elif isinstance(error, ConnectionError):
            code = ErrorCode.CONNECTION_ERROR
            severity = ErrorSeverity.HIGH
        elif isinstance(error, TimeoutError):
            code = ErrorCode.QUERY_TIMEOUT
            severity = ErrorSeverity.MEDIUM
        else:
            code = ErrorCode.INTERNAL_ERROR
            severity = ErrorSeverity.HIGH
        
        return ErrorDetail(
            code=code,
            message=str(error),
            severity=severity,
            context=context or {},
            stack_trace=traceback.format_exc(),
            details={
                'error_type': type(error).__name__,
                'module': type(error).__module__
            }
        )
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """
        重要度からログレベルを決定
        """
        mapping = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }
        return mapping.get(severity, logging.ERROR)
    
    def _log_error(self, error_detail: ErrorDetail, log_level: int):
        """
        エラーをログ出力
        """
        log_message = {
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'error': error_detail.to_dict()
        }
        
        logger.log(
            log_level,
            f"Error occurred: {error_detail.message}",
            extra={'error_detail': log_message}
        )
    
    def _update_statistics(self, error_detail: ErrorDetail):
        """
        エラー統計を更新
        """
        # エラーカウント
        error_code = error_detail.code.value
        self.error_count[error_code] = self.error_count.get(error_code, 0) + 1
        
        # 最近のエラーを保持
        self.last_errors.append({
            'timestamp': datetime.utcnow().isoformat(),
            'code': error_code,
            'message': error_detail.message[:100]  # 最初の100文字
        })
        
        # サイズ制限
        if len(self.last_errors) > self.max_last_errors:
            self.last_errors = self.last_errors[-self.max_last_errors:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        エラー統計を取得
        """
        return {
            'error_count': self.error_count,
            'last_errors': self.last_errors,
            'total_errors': sum(self.error_count.values())
        }
    
    def clear_statistics(self):
        """
        統計をクリア
        """
        self.error_count.clear()
        self.last_errors.clear()


# グローバルエラーハンドラー
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """エラーハンドラーを取得"""
    return _error_handler


@contextmanager
def error_context(
    operation: str,
    reraise: bool = True,
    default_return: Any = None,
    error_handler: Optional[ErrorHandler] = None
):
    """
    エラーコンテキストマネージャー
    
    Args:
        operation: 操作名
        reraise: 例外を再スローするか
        default_return: エラー時のデフォルト戻り値
        error_handler: エラーハンドラー
        
    Example:
        ```python
        with error_context('database_query', reraise=False):
            result = db.query(...)
        ```
    """
    handler = error_handler or _error_handler
    
    try:
        yield
    except Exception as e:
        handler.handle_error(
            e,
            context={'operation': operation}
        )
        
        if reraise:
            raise
        else:
            return default_return


def handle_errors(
    operation: Optional[str] = None,
    reraise: bool = True,
    default_return: Any = None,
    convert_to: Optional[Type[MakotoError]] = None
):
    """
    エラーハンドリングデコレーター
    
    Args:
        operation: 操作名
        reraise: 例外を再スローするか
        default_return: エラー時のデフォルト戻り値
        convert_to: 変換先のエラークラス
        
    Example:
        ```python
        @handle_errors(operation='get_user', convert_to=DatabaseError)
        def get_user(user_id: str):
            return db.get(user_id)
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            
            try:
                return func(*args, **kwargs)
            except MakotoError:
                # 既にMakotoErrorの場合はそのまま
                raise
            except Exception as e:
                # エラーハンドリング
                _error_handler.handle_error(
                    e,
                    context={
                        'operation': op_name,
                        'function': func.__name__,
                        'module': func.__module__
                    }
                )
                
                # エラー変換
                if convert_to:
                    converted_error = convert_to(
                        str(e),
                        cause=e
                    )
                    raise converted_error
                
                if reraise:
                    raise
                else:
                    return default_return
        
        # 非同期関数の場合
        if asyncio.iscoroutinefunction(func):
            import asyncio
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                op_name = operation or func.__name__
                
                try:
                    return await func(*args, **kwargs)
                except MakotoError:
                    raise
                except Exception as e:
                    _error_handler.handle_error(
                        e,
                        context={
                            'operation': op_name,
                            'function': func.__name__,
                            'module': func.__module__,
                            'is_async': True
                        }
                    )
                    
                    if convert_to:
                        converted_error = convert_to(
                            str(e),
                            cause=e
                        )
                        raise converted_error
                    
                    if reraise:
                        raise
                    else:
                        return default_return
            
            return async_wrapper
        
        return wrapper
    
    return decorator


def retry_on_error(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    エラー時にリトライするデコレーター
    
    Args:
        max_attempts: 最大試行回数
        delay: 初回待機時間（秒）
        backoff: バックオフ係数
        exceptions: リトライ対象の例外
        on_retry: リトライ時のコールバック
        
    Example:
        ```python
        @retry_on_error(max_attempts=3, exceptions=(ConnectionError,))
        def connect_to_service():
            return service.connect()
        ```
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        if on_retry:
                            on_retry(attempt + 1, e)
                        
                        logger.warning(
                            f"リトライ {attempt + 1}/{max_attempts}: {func.__name__}",
                            extra={'error': str(e)}
                        )
                        
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        # 最後の試行で失敗
                        logger.error(
                            f"リトライ失敗: {func.__name__} ({max_attempts}回試行)",
                            extra={'error': str(e)}
                        )
            
            # すべて失敗した場合
            if last_exception:
                raise last_exception
        
        # 非同期関数の場合
        if asyncio.iscoroutinefunction(func):
            import asyncio
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                current_delay = delay
                last_exception = None
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        
                        if attempt < max_attempts - 1:
                            if on_retry:
                                on_retry(attempt + 1, e)
                            
                            logger.warning(
                                f"リトライ {attempt + 1}/{max_attempts}: {func.__name__}",
                                extra={'error': str(e)}
                            )
                            
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(
                                f"リトライ失敗: {func.__name__} ({max_attempts}回試行)",
                                extra={'error': str(e)}
                            )
                
                if last_exception:
                    raise last_exception
            
            return async_wrapper
        
        return wrapper
    
    return decorator


def format_error_response(
    error: Union[Exception, ErrorDetail],
    request_id: Optional[str] = None,
    include_stack: bool = False
) -> Dict[str, Any]:
    """
    APIレスポンス用にエラーをフォーマット
    
    Args:
        error: エラーまたはエラー詳細
        request_id: リクエストID
        include_stack: スタックトレースを含めるか
        
    Returns:
        APIレスポンス用の辞書
    """
    if isinstance(error, ErrorDetail):
        error_detail = error
    elif isinstance(error, MakotoError):
        error_detail = error.error_detail
    else:
        error_detail = _error_handler._convert_to_error_detail(error)
    
    response = {
        'success': False,
        'error': {
            'code': error_detail.code.value,
            'message': error_detail.user_message or error_detail.message,
            'severity': error_detail.severity.value
        }
    }
    
    if request_id:
        response['request_id'] = request_id
    
    if error_detail.details:
        response['error']['details'] = error_detail.details
    
    if error_detail.recovery_hints:
        response['error']['recovery_hints'] = error_detail.recovery_hints
    
    if include_stack and error_detail.stack_trace:
        response['error']['stack_trace'] = error_detail.stack_trace
    
    return response