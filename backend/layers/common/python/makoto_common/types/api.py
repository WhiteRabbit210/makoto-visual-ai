"""
API型定義
APIリクエスト/レスポンスの型定義を提供
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar
from uuid import uuid4

from .primitives import TenantId, UserId

T = TypeVar('T')


class ErrorCode(Enum):
    """エラーコード"""
    # 認証・認可
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # リソース
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # バリデーション
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_FORMAT = "INVALID_FORMAT"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    
    # システム
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"


@dataclass
class BaseRequest:
    """
    基底リクエストクラス
    すべてのAPIリクエストの基底
    """
    request_id: str = field(default_factory=lambda: str(uuid4()))  # リクエストID
    timestamp: datetime = field(default_factory=datetime.utcnow)  # タイムスタンプ
    tenant_id: Optional[TenantId] = None  # テナントID
    user_id: Optional[UserId] = None  # ユーザーID


@dataclass
class BaseResponse(Generic[T]):
    """
    基底レスポンスクラス
    すべてのAPIレスポンスの基底
    """
    success: bool  # 成功フラグ
    data: Optional[T] = None  # レスポンスデータ
    error: Optional['ErrorDetail'] = None  # エラー詳細
    request_id: str = field(default_factory=lambda: str(uuid4()))  # リクエストID
    timestamp: datetime = field(default_factory=datetime.utcnow)  # タイムスタンプ
    
    @classmethod
    def ok(cls, data: T, request_id: Optional[str] = None) -> 'BaseResponse[T]':
        """成功レスポンスを作成"""
        return cls(
            success=True,
            data=data,
            request_id=request_id or str(uuid4())
        )
    
    @classmethod
    def error(
        cls,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> 'BaseResponse[T]':
        """エラーレスポンスを作成"""
        return cls(
            success=False,
            error=ErrorDetail(
                code=error_code,
                message=message,
                details=details
            ),
            request_id=request_id or str(uuid4())
        )


@dataclass
class PaginationRequest(BaseRequest):
    """
    ページネーションリクエスト
    一覧取得APIで使用
    """
    page: int = 1  # ページ番号（1から開始）
    limit: int = 20  # 取得件数
    sort_by: Optional[str] = None  # ソートキー
    order: str = "asc"  # ソート順 (asc, desc)
    
    def __post_init__(self):
        """バリデーション"""
        if self.page < 1:
            self.page = 1
        if self.limit < 1:
            self.limit = 1
        elif self.limit > 100:
            self.limit = 100
        if self.order not in ("asc", "desc"):
            self.order = "asc"


@dataclass
class PaginationMeta:
    """ページネーションメタデータ"""
    total: int  # 総件数
    page: int  # 現在のページ
    limit: int  # ページあたりの件数
    pages: int  # 総ページ数
    has_next: bool  # 次ページの有無
    has_prev: bool  # 前ページの有無
    
    @classmethod
    def create(cls, total: int, page: int, limit: int) -> 'PaginationMeta':
        """メタデータを作成"""
        pages = (total + limit - 1) // limit if limit > 0 else 1
        return cls(
            total=total,
            page=page,
            limit=limit,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )


@dataclass
class PaginatedResponse(BaseResponse[T], Generic[T]):
    """
    ページネーションレスポンス
    一覧取得APIで使用
    """
    items: List[T] = field(default_factory=list)  # アイテムリスト
    meta: Optional[PaginationMeta] = None  # ページネーション情報
    
    @classmethod
    def paginate(
        cls,
        items: List[T],
        total: int,
        page: int,
        limit: int,
        request_id: Optional[str] = None
    ) -> 'PaginatedResponse[T]':
        """ページネーションレスポンスを作成"""
        return cls(
            success=True,
            data=None,  # itemsフィールドを使用
            items=items,
            meta=PaginationMeta.create(total, page, limit),
            request_id=request_id or str(uuid4())
        )


@dataclass
class ErrorDetail:
    """
    エラー詳細
    エラーレスポンスで使用
    """
    code: ErrorCode  # エラーコード
    message: str  # エラーメッセージ
    field: Optional[str] = None  # エラーが発生したフィールド
    details: Optional[Dict[str, Any]] = None  # 詳細情報
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        result = {
            "code": self.code.value,
            "message": self.message
        }
        if self.field:
            result["field"] = self.field
        if self.details:
            result["details"] = self.details
        return result


@dataclass
class ErrorResponse(BaseResponse[None]):
    """
    エラーレスポンス
    エラー時の標準レスポンス
    """
    success: bool = False  # 常にFalse
    errors: List[ErrorDetail] = field(default_factory=list)  # エラーリスト
    
    @classmethod
    def validation_error(
        cls,
        errors: List[Dict[str, Any]],
        request_id: Optional[str] = None
    ) -> 'ErrorResponse':
        """バリデーションエラーレスポンスを作成"""
        error_details = []
        for error in errors:
            error_details.append(
                ErrorDetail(
                    code=ErrorCode.VALIDATION_ERROR,
                    message=error.get("message", "Validation error"),
                    field=error.get("field"),
                    details=error.get("details")
                )
            )
        return cls(
            errors=error_details,
            request_id=request_id or str(uuid4())
        )


@dataclass
class BatchRequest(BaseRequest, Generic[T]):
    """
    バッチリクエスト
    複数のアイテムを一括処理
    """
    items: List[T] = field(default_factory=list)  # 処理対象アイテム
    continue_on_error: bool = False  # エラー時も継続するか
    
    def __post_init__(self):
        """バリデーション"""
        super().__post_init__()
        if not self.items:
            raise ValueError("items cannot be empty")
        if len(self.items) > 1000:
            raise ValueError("items cannot exceed 1000")


@dataclass
class BatchResponse(BaseResponse[T], Generic[T]):
    """
    バッチレスポンス
    複数のアイテムの処理結果
    """
    succeeded: List[T] = field(default_factory=list)  # 成功アイテム
    failed: List[Dict[str, Any]] = field(default_factory=list)  # 失敗アイテム
    total: int = 0  # 総件数
    success_count: int = 0  # 成功件数
    failure_count: int = 0  # 失敗件数
    
    @classmethod
    def create(
        cls,
        succeeded: List[T],
        failed: List[Dict[str, Any]],
        request_id: Optional[str] = None
    ) -> 'BatchResponse[T]':
        """バッチレスポンスを作成"""
        success_count = len(succeeded)
        failure_count = len(failed)
        return cls(
            success=failure_count == 0,
            succeeded=succeeded,
            failed=failed,
            total=success_count + failure_count,
            success_count=success_count,
            failure_count=failure_count,
            request_id=request_id or str(uuid4())
        )


@dataclass
class StreamingResponse(BaseResponse[T], Generic[T]):
    """
    ストリーミングレスポンス
    Server-Sent Events用
    """
    event_type: str = ""  # イベントタイプ
    event_id: Optional[str] = None  # イベントID
    retry: Optional[int] = None  # リトライ間隔（ミリ秒）
    
    def to_sse(self) -> str:
        """SSE形式に変換"""
        lines = []
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        if self.event_type:
            lines.append(f"event: {self.event_type}")
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        if self.data:
            import json
            lines.append(f"data: {json.dumps(self.data)}")
        lines.append("")  # 空行で終了
        return "\n".join(lines)


# SSEイベント型定義（ドキュメント準拠）
@dataclass
class GeneratedImage:
    """生成された画像"""
    url: str
    prompt: str
    size: str
    style: Optional[str] = None


@dataclass
class TextChunkEvent:
    """テキストチャンクイベント"""
    type: str = "text"
    content: str = ""


@dataclass
class ImageGeneratingEvent:
    """画像生成開始イベント"""
    type: str = "generating_image"
    generating_image: bool = True


@dataclass
class ImageGeneratedEvent:
    """画像生成完了イベント"""
    type: str = "images"
    images: List[GeneratedImage] = field(default_factory=list)


@dataclass
class StreamErrorEvent:
    """ストリームエラーイベント"""
    type: str = "error"
    error: str = ""


@dataclass
class StreamCompleteEvent:
    """ストリーム完了イベント"""
    type: str = "done"
    done: bool = True
    chat_id: str = ""
    message_id: str = ""