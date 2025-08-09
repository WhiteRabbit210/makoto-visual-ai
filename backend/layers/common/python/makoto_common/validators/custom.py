"""
カスタムバリデーター
様々な入力値検証のためのバリデーター
"""

import re
import json
from typing import Any, Optional, List, Pattern, Union
from datetime import datetime, date
from urllib.parse import urlparse
import uuid
import phonenumbers
from email_validator import validate_email, EmailNotValidError

from ..errors import ValidationError


class BaseValidator:
    """
    基底バリデータークラス
    """
    
    def __init__(self, error_message: Optional[str] = None):
        """
        初期化
        
        Args:
            error_message: カスタムエラーメッセージ
        """
        self.error_message = error_message
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """
        値を検証
        
        Args:
            value: 検証する値
            field_name: フィールド名
            
        Returns:
            検証成功の場合True
            
        Raises:
            ValidationError: 検証失敗
        """
        raise NotImplementedError
    
    def get_error_message(self, value: Any, field_name: Optional[str] = None) -> str:
        """
        エラーメッセージを取得
        
        Args:
            value: 検証した値
            field_name: フィールド名
            
        Returns:
            エラーメッセージ
        """
        if self.error_message:
            return self.error_message
        
        if field_name:
            return f"{field_name}の値が不正です"
        else:
            return "値が不正です"


class EmailValidator(BaseValidator):
    """
    メールアドレスバリデーター
    """
    
    def __init__(
        self,
        check_deliverability: bool = False,
        whitelist_domains: Optional[List[str]] = None,
        blacklist_domains: Optional[List[str]] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            check_deliverability: 配達可能性をチェックするか
            whitelist_domains: 許可するドメインリスト
            blacklist_domains: 拒否するドメインリスト
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.check_deliverability = check_deliverability
        self.whitelist_domains = whitelist_domains
        self.blacklist_domains = blacklist_domains
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """メールアドレスを検証"""
        if not value:
            raise ValidationError(
                "メールアドレスが必要です",
                field=field_name,
                value=value
            )
        
        try:
            # email-validatorを使用した検証
            validation = validate_email(
                value,
                check_deliverability=self.check_deliverability
            )
            email = validation.email
            domain = email.split('@')[1]
            
            # ホワイトリストチェック
            if self.whitelist_domains and domain not in self.whitelist_domains:
                raise ValidationError(
                    f"ドメイン {domain} は許可されていません",
                    field=field_name,
                    value=value
                )
            
            # ブラックリストチェック
            if self.blacklist_domains and domain in self.blacklist_domains:
                raise ValidationError(
                    f"ドメイン {domain} は拒否されています",
                    field=field_name,
                    value=value
                )
            
            return True
            
        except EmailNotValidError as e:
            raise ValidationError(
                self.error_message or str(e),
                field=field_name,
                value=value
            )


class PhoneValidator(BaseValidator):
    """
    電話番号バリデーター
    """
    
    def __init__(
        self,
        region: str = 'JP',
        allowed_regions: Optional[List[str]] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            region: デフォルトリージョン
            allowed_regions: 許可するリージョンリスト
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.region = region
        self.allowed_regions = allowed_regions or [region]
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """電話番号を検証"""
        if not value:
            raise ValidationError(
                "電話番号が必要です",
                field=field_name,
                value=value
            )
        
        try:
            # phonenumbersを使用した検証
            parsed = phonenumbers.parse(value, self.region)
            
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError(
                    "無効な電話番号です",
                    field=field_name,
                    value=value
                )
            
            # リージョンチェック
            region_code = phonenumbers.region_code_for_number(parsed)
            if region_code not in self.allowed_regions:
                raise ValidationError(
                    f"リージョン {region_code} は許可されていません",
                    field=field_name,
                    value=value
                )
            
            return True
            
        except phonenumbers.NumberParseException as e:
            raise ValidationError(
                self.error_message or f"電話番号の解析に失敗: {e}",
                field=field_name,
                value=value
            )


class URLValidator(BaseValidator):
    """
    URLバリデーター
    """
    
    def __init__(
        self,
        schemes: Optional[List[str]] = None,
        require_tld: bool = True,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            schemes: 許可するスキーム（デフォルト: http, https）
            require_tld: TLDを必須とするか
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.schemes = schemes or ['http', 'https']
        self.require_tld = require_tld
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """URLを検証"""
        if not value:
            raise ValidationError(
                "URLが必要です",
                field=field_name,
                value=value
            )
        
        try:
            result = urlparse(str(value))
            
            # スキームチェック
            if result.scheme not in self.schemes:
                raise ValidationError(
                    f"スキーム {result.scheme} は許可されていません",
                    field=field_name,
                    value=value
                )
            
            # ホスト名チェック
            if not result.netloc:
                raise ValidationError(
                    "ホスト名が必要です",
                    field=field_name,
                    value=value
                )
            
            # TLDチェック
            if self.require_tld and '.' not in result.netloc:
                raise ValidationError(
                    "有効なドメイン名が必要です",
                    field=field_name,
                    value=value
                )
            
            return True
            
        except Exception as e:
            raise ValidationError(
                self.error_message or f"URL解析エラー: {e}",
                field=field_name,
                value=value
            )


class UUIDValidator(BaseValidator):
    """
    UUIDバリデーター
    """
    
    def __init__(
        self,
        version: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            version: UUIDバージョン（1, 3, 4, 5）
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.version = version
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """UUIDを検証"""
        if not value:
            raise ValidationError(
                "UUIDが必要です",
                field=field_name,
                value=value
            )
        
        try:
            uuid_obj = uuid.UUID(str(value))
            
            # バージョンチェック
            if self.version and uuid_obj.version != self.version:
                raise ValidationError(
                    f"UUID version {self.version} が必要です",
                    field=field_name,
                    value=value
                )
            
            return True
            
        except (ValueError, AttributeError) as e:
            raise ValidationError(
                self.error_message or f"無効なUUID: {e}",
                field=field_name,
                value=value
            )


class DateTimeValidator(BaseValidator):
    """
    日時バリデーター
    """
    
    def __init__(
        self,
        format: str = '%Y-%m-%d %H:%M:%S',
        min_value: Optional[datetime] = None,
        max_value: Optional[datetime] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            format: 日時フォーマット
            min_value: 最小値
            max_value: 最大値
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.format = format
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """日時を検証"""
        if not value:
            raise ValidationError(
                "日時が必要です",
                field=field_name,
                value=value
            )
        
        # 既にdatetimeオブジェクトの場合
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, date):
            dt = datetime.combine(value, datetime.min.time())
        else:
            # 文字列から解析
            try:
                dt = datetime.strptime(str(value), self.format)
            except ValueError as e:
                raise ValidationError(
                    self.error_message or f"日時フォーマットエラー: {e}",
                    field=field_name,
                    value=value
                )
        
        # 範囲チェック
        if self.min_value and dt < self.min_value:
            raise ValidationError(
                f"日時は {self.min_value} 以降である必要があります",
                field=field_name,
                value=value
            )
        
        if self.max_value and dt > self.max_value:
            raise ValidationError(
                f"日時は {self.max_value} 以前である必要があります",
                field=field_name,
                value=value
            )
        
        return True


class JSONValidator(BaseValidator):
    """
    JSONバリデーター
    """
    
    def __init__(
        self,
        schema: Optional[dict] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            schema: JSONスキーマ
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.schema = schema
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """JSONを検証"""
        if not value:
            raise ValidationError(
                "JSONデータが必要です",
                field=field_name,
                value=value
            )
        
        # 文字列の場合はパース
        if isinstance(value, str):
            try:
                data = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValidationError(
                    self.error_message or f"JSON解析エラー: {e}",
                    field=field_name,
                    value=value
                )
        else:
            data = value
        
        # スキーマ検証
        if self.schema:
            import jsonschema
            try:
                jsonschema.validate(data, self.schema)
            except jsonschema.ValidationError as e:
                raise ValidationError(
                    self.error_message or f"JSONスキーマ検証エラー: {e.message}",
                    field=field_name,
                    value=value
                )
        
        return True


class RegexValidator(BaseValidator):
    """
    正規表現バリデーター
    """
    
    def __init__(
        self,
        pattern: Union[str, Pattern],
        flags: int = 0,
        inverse: bool = False,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            pattern: 正規表現パターン
            flags: 正規表現フラグ
            inverse: マッチしない場合に成功とするか
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern, flags)
        else:
            self.pattern = pattern
        self.inverse = inverse
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """正規表現で検証"""
        if not value:
            raise ValidationError(
                "値が必要です",
                field=field_name,
                value=value
            )
        
        match = self.pattern.search(str(value))
        
        if self.inverse:
            if match:
                raise ValidationError(
                    self.error_message or f"パターン {self.pattern.pattern} にマッチしてはいけません",
                    field=field_name,
                    value=value
                )
        else:
            if not match:
                raise ValidationError(
                    self.error_message or f"パターン {self.pattern.pattern} にマッチする必要があります",
                    field=field_name,
                    value=value
                )
        
        return True


class LengthValidator(BaseValidator):
    """
    長さバリデーター
    """
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        exact_length: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            min_length: 最小長
            max_length: 最大長
            exact_length: 正確な長さ
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.min_length = min_length
        self.max_length = max_length
        self.exact_length = exact_length
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """長さを検証"""
        if value is None:
            length = 0
        elif hasattr(value, '__len__'):
            length = len(value)
        else:
            length = len(str(value))
        
        # 正確な長さチェック
        if self.exact_length is not None and length != self.exact_length:
            raise ValidationError(
                self.error_message or f"長さは {self.exact_length} である必要があります",
                field=field_name,
                value=value
            )
        
        # 最小長チェック
        if self.min_length is not None and length < self.min_length:
            raise ValidationError(
                self.error_message or f"長さは {self.min_length} 以上である必要があります",
                field=field_name,
                value=value
            )
        
        # 最大長チェック
        if self.max_length is not None and length > self.max_length:
            raise ValidationError(
                self.error_message or f"長さは {self.max_length} 以下である必要があります",
                field=field_name,
                value=value
            )
        
        return True


class RangeValidator(BaseValidator):
    """
    範囲バリデーター
    """
    
    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            min_value: 最小値
            max_value: 最大値
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """範囲を検証"""
        if value is None:
            raise ValidationError(
                "値が必要です",
                field=field_name,
                value=value
            )
        
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                "数値が必要です",
                field=field_name,
                value=value
            )
        
        # 最小値チェック
        if self.min_value is not None and num_value < self.min_value:
            raise ValidationError(
                self.error_message or f"値は {self.min_value} 以上である必要があります",
                field=field_name,
                value=value
            )
        
        # 最大値チェック
        if self.max_value is not None and num_value > self.max_value:
            raise ValidationError(
                self.error_message or f"値は {self.max_value} 以下である必要があります",
                field=field_name,
                value=value
            )
        
        return True


class ChoiceValidator(BaseValidator):
    """
    選択肢バリデーター
    """
    
    def __init__(
        self,
        choices: List[Any],
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            choices: 選択肢リスト
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.choices = choices
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """選択肢を検証"""
        if value not in self.choices:
            raise ValidationError(
                self.error_message or f"値は {self.choices} のいずれかである必要があります",
                field=field_name,
                value=value
            )
        
        return True


class FileValidator(BaseValidator):
    """
    ファイルバリデーター
    """
    
    def __init__(
        self,
        allowed_extensions: Optional[List[str]] = None,
        allowed_mimetypes: Optional[List[str]] = None,
        max_size: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            allowed_extensions: 許可する拡張子リスト
            allowed_mimetypes: 許可するMIMEタイプリスト
            max_size: 最大ファイルサイズ（バイト）
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.allowed_extensions = allowed_extensions
        self.allowed_mimetypes = allowed_mimetypes
        self.max_size = max_size
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """ファイルを検証"""
        if not value:
            raise ValidationError(
                "ファイルが必要です",
                field=field_name,
                value=value
            )
        
        # ファイル名とサイズの取得
        if hasattr(value, 'filename'):
            filename = value.filename
        elif isinstance(value, dict) and 'filename' in value:
            filename = value['filename']
        else:
            filename = str(value)
        
        if hasattr(value, 'size'):
            size = value.size
        elif isinstance(value, dict) and 'size' in value:
            size = value['size']
        else:
            size = None
        
        # 拡張子チェック
        if self.allowed_extensions:
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            if ext not in self.allowed_extensions:
                raise ValidationError(
                    self.error_message or f"拡張子 {ext} は許可されていません",
                    field=field_name,
                    value=value
                )
        
        # MIMEタイプチェック（辞書形式の場合）
        if self.allowed_mimetypes and isinstance(value, dict) and 'mimetype' in value:
            if value['mimetype'] not in self.allowed_mimetypes:
                raise ValidationError(
                    self.error_message or f"MIMEタイプ {value['mimetype']} は許可されていません",
                    field=field_name,
                    value=value
                )
        
        # サイズチェック
        if self.max_size and size and size > self.max_size:
            raise ValidationError(
                self.error_message or f"ファイルサイズは {self.max_size} バイト以下である必要があります",
                field=field_name,
                value=value
            )
        
        return True