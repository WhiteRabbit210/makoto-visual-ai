"""
エラークラス定義
共通エラーとカスタム例外を定義
"""

from typing import Any, Dict, Optional


class MakotoError(Exception):
    """
    MAKOTO基底エラークラス
    すべてのカスタムエラーの基底クラス
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        エラーを初期化
        
        Args:
            message: エラーメッセージ
            error_code: エラーコード
            status_code: HTTPステータスコード
            details: 詳細情報
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        エラーを辞書形式に変換
        
        Returns:
            エラー情報の辞書
        """
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }


class ValidationError(MakotoError):
    """
    バリデーションエラー
    入力値の検証に失敗した場合
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        バリデーションエラーを初期化
        
        Args:
            message: エラーメッセージ
            field: エラーが発生したフィールド名
            value: 無効な値
            details: 詳細情報
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["value"] = str(value)
        
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=error_details
        )


class AuthenticationError(MakotoError):
    """
    認証エラー
    認証に失敗した場合
    """
    
    def __init__(
        self,
        message: str = "認証に失敗しました",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        認証エラーを初期化
        
        Args:
            message: エラーメッセージ
            details: 詳細情報
        """
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(MakotoError):
    """
    認可エラー
    権限が不足している場合
    """
    
    def __init__(
        self,
        message: str = "このリソースへのアクセス権限がありません",
        resource: Optional[str] = None,
        required_permission: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        認可エラーを初期化
        
        Args:
            message: エラーメッセージ
            resource: アクセスしようとしたリソース
            required_permission: 必要な権限
            details: 詳細情報
        """
        error_details = details or {}
        if resource:
            error_details["resource"] = resource
        if required_permission:
            error_details["required_permission"] = required_permission
        
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=error_details
        )


class NotFoundError(MakotoError):
    """
    リソース未検出エラー
    リソースが見つからない場合
    """
    
    def __init__(
        self,
        message: str = "リソースが見つかりません",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        未検出エラーを初期化
        
        Args:
            message: エラーメッセージ
            resource_type: リソースタイプ
            resource_id: リソースID
            details: 詳細情報
        """
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=404,
            details=error_details
        )


class ConflictError(MakotoError):
    """
    競合エラー
    リソースの状態が競合している場合
    """
    
    def __init__(
        self,
        message: str = "リソースの状態が競合しています",
        conflict_type: Optional[str] = None,
        existing_value: Any = None,
        new_value: Any = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        競合エラーを初期化
        
        Args:
            message: エラーメッセージ
            conflict_type: 競合タイプ
            existing_value: 既存の値
            new_value: 新しい値
            details: 詳細情報
        """
        error_details = details or {}
        if conflict_type:
            error_details["conflict_type"] = conflict_type
        if existing_value is not None:
            error_details["existing_value"] = str(existing_value)
        if new_value is not None:
            error_details["new_value"] = str(new_value)
        
        super().__init__(
            message=message,
            error_code="CONFLICT",
            status_code=409,
            details=error_details
        )


class RateLimitError(MakotoError):
    """
    レート制限エラー
    API呼び出し回数が制限を超えた場合
    """
    
    def __init__(
        self,
        message: str = "レート制限を超えました",
        limit: Optional[int] = None,
        window: Optional[int] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        レート制限エラーを初期化
        
        Args:
            message: エラーメッセージ
            limit: 制限回数
            window: ウィンドウサイズ（秒）
            retry_after: リトライ可能になるまでの秒数
            details: 詳細情報
        """
        error_details = details or {}
        if limit:
            error_details["limit"] = limit
        if window:
            error_details["window"] = window
        if retry_after:
            error_details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=error_details
        )


class ServiceUnavailableError(MakotoError):
    """
    サービス利用不可エラー
    サービスが一時的に利用できない場合
    """
    
    def __init__(
        self,
        message: str = "サービスが一時的に利用できません",
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        サービス利用不可エラーを初期化
        
        Args:
            message: エラーメッセージ
            service_name: サービス名
            retry_after: リトライ可能になるまでの秒数
            details: 詳細情報
        """
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name
        if retry_after:
            error_details["retry_after"] = retry_after
        
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=error_details
        )