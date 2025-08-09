"""
複合バリデーター
複数のバリデーターを組み合わせた検証
"""

from typing import Any, List, Dict, Optional, Callable, Union
from dataclasses import fields, is_dataclass

from ..errors import ValidationError
from .custom import BaseValidator


class CompositeValidator(BaseValidator):
    """
    複合バリデーター基底クラス
    """
    
    def __init__(
        self,
        validators: List[BaseValidator],
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            validators: バリデーターリスト
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.validators = validators


class AllValidator(CompositeValidator):
    """
    すべてのバリデーターが成功する必要がある複合バリデーター
    """
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """すべてのバリデーターで検証"""
        errors = []
        
        for validator in self.validators:
            try:
                validator.validate(value, field_name)
            except ValidationError as e:
                errors.append(str(e))
        
        if errors:
            raise ValidationError(
                self.error_message or f"検証エラー: {'; '.join(errors)}",
                field=field_name,
                value=value,
                details={'errors': errors}
            )
        
        return True


class AnyValidator(CompositeValidator):
    """
    いずれかのバリデーターが成功すればよい複合バリデーター
    """
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """いずれかのバリデーターで検証"""
        errors = []
        
        for validator in self.validators:
            try:
                validator.validate(value, field_name)
                return True  # 1つでも成功すればOK
            except ValidationError as e:
                errors.append(str(e))
        
        # すべて失敗した場合
        raise ValidationError(
            self.error_message or f"いずれかの条件を満たす必要があります: {'; '.join(errors)}",
            field=field_name,
            value=value,
            details={'errors': errors}
        )


class ConditionalValidator(BaseValidator):
    """
    条件付きバリデーター
    条件が満たされた場合のみ検証を実行
    """
    
    def __init__(
        self,
        condition: Callable[[Any], bool],
        validator: BaseValidator,
        else_validator: Optional[BaseValidator] = None,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            condition: 条件関数
            validator: 条件が真の場合のバリデーター
            else_validator: 条件が偽の場合のバリデーター
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.condition = condition
        self.validator = validator
        self.else_validator = else_validator
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """条件に基づいて検証"""
        if self.condition(value):
            return self.validator.validate(value, field_name)
        elif self.else_validator:
            return self.else_validator.validate(value, field_name)
        
        return True


class DependentValidator(BaseValidator):
    """
    依存バリデーター
    他のフィールドの値に依存した検証
    """
    
    def __init__(
        self,
        depends_on: str,
        condition: Callable[[Any, Any], bool],
        validator: BaseValidator,
        error_message: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            depends_on: 依存するフィールド名
            condition: 条件関数（依存フィールド値, 対象値）
            validator: 条件が真の場合のバリデーター
            error_message: カスタムエラーメッセージ
        """
        super().__init__(error_message)
        self.depends_on = depends_on
        self.condition = condition
        self.validator = validator
    
    def validate_with_context(
        self,
        value: Any,
        context: Dict[str, Any],
        field_name: Optional[str] = None
    ) -> bool:
        """
        コンテキストを使用して検証
        
        Args:
            value: 検証する値
            context: 他のフィールドを含むコンテキスト
            field_name: フィールド名
            
        Returns:
            検証成功の場合True
        """
        if self.depends_on not in context:
            raise ValidationError(
                f"依存フィールド {self.depends_on} が見つかりません",
                field=field_name,
                value=value
            )
        
        dependent_value = context[self.depends_on]
        
        if self.condition(dependent_value, value):
            return self.validator.validate(value, field_name)
        
        return True
    
    def validate(self, value: Any, field_name: Optional[str] = None) -> bool:
        """通常の検証（コンテキストなし）"""
        # コンテキストなしでは検証をスキップ
        return True


class FieldValidator:
    """
    フィールドバリデーター
    辞書の特定フィールドを検証
    """
    
    def __init__(
        self,
        field_validators: Dict[str, Union[BaseValidator, List[BaseValidator]]],
        allow_extra: bool = False,
        require_all: bool = True
    ):
        """
        初期化
        
        Args:
            field_validators: フィールド名とバリデーターのマッピング
            allow_extra: 定義外のフィールドを許可するか
            require_all: すべてのフィールドを必須とするか
        """
        self.field_validators = field_validators
        self.allow_extra = allow_extra
        self.require_all = require_all
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        辞書データを検証
        
        Args:
            data: 検証するデータ
            
        Returns:
            検証成功の場合True
            
        Raises:
            ValidationError: 検証失敗
        """
        if not isinstance(data, dict):
            raise ValidationError(f"辞書が必要です: {type(data)}")
        
        errors = {}
        
        # 必須フィールドチェック
        if self.require_all:
            missing = set(self.field_validators.keys()) - set(data.keys())
            if missing:
                for field in missing:
                    errors[field] = f"必須フィールド {field} がありません"
        
        # 各フィールドの検証
        for field_name, value in data.items():
            if field_name in self.field_validators:
                validators = self.field_validators[field_name]
                if not isinstance(validators, list):
                    validators = [validators]
                
                for validator in validators:
                    try:
                        # DependentValidatorの場合はコンテキスト付きで検証
                        if isinstance(validator, DependentValidator):
                            validator.validate_with_context(value, data, field_name)
                        else:
                            validator.validate(value, field_name)
                    except ValidationError as e:
                        if field_name not in errors:
                            errors[field_name] = []
                        errors[field_name].append(str(e))
            elif not self.allow_extra:
                errors[field_name] = f"未定義のフィールド: {field_name}"
        
        if errors:
            raise ValidationError(
                "フィールド検証エラー",
                details={'field_errors': errors}
            )
        
        return True


class ModelValidator:
    """
    モデルバリデーター
    dataclassやPydanticモデルの検証
    """
    
    def __init__(
        self,
        model_class: type,
        field_validators: Optional[Dict[str, BaseValidator]] = None,
        custom_validators: Optional[List[Callable]] = None
    ):
        """
        初期化
        
        Args:
            model_class: モデルクラス
            field_validators: 追加のフィールドバリデーター
            custom_validators: カスタム検証関数リスト
        """
        self.model_class = model_class
        self.field_validators = field_validators or {}
        self.custom_validators = custom_validators or []
    
    def validate(self, instance: Any) -> bool:
        """
        モデルインスタンスを検証
        
        Args:
            instance: 検証するインスタンス
            
        Returns:
            検証成功の場合True
            
        Raises:
            ValidationError: 検証失敗
        """
        if not isinstance(instance, self.model_class):
            raise ValidationError(
                f"型が一致しません: {type(instance)} != {self.model_class}"
            )
        
        errors = {}
        
        # dataclassの場合
        if is_dataclass(instance):
            for field in fields(instance):
                field_name = field.name
                value = getattr(instance, field_name)
                
                # フィールドバリデーター実行
                if field_name in self.field_validators:
                    try:
                        self.field_validators[field_name].validate(value, field_name)
                    except ValidationError as e:
                        errors[field_name] = str(e)
                
                # 型チェック
                if field.type and not self._check_type(value, field.type):
                    errors[field_name] = f"型が一致しません: {type(value)} != {field.type}"
        
        # Pydanticモデルの場合
        elif hasattr(instance, 'model_validate'):
            try:
                instance.model_validate(instance.model_dump())
            except Exception as e:
                errors['_model'] = str(e)
        
        # カスタムバリデーター実行
        for validator_func in self.custom_validators:
            try:
                validator_func(instance)
            except ValidationError as e:
                errors['_custom'] = str(e)
            except Exception as e:
                errors['_custom'] = f"カスタム検証エラー: {e}"
        
        if errors:
            raise ValidationError(
                "モデル検証エラー",
                details={'validation_errors': errors}
            )
        
        return True
    
    def _check_type(self, value: Any, expected_type: type) -> bool:
        """
        型チェック
        
        Args:
            value: チェックする値
            expected_type: 期待する型
            
        Returns:
            型が一致する場合True
        """
        # Noneの場合はOptionalかチェック
        if value is None:
            return self._is_optional(expected_type)
        
        # Union型の場合
        if hasattr(expected_type, '__origin__'):
            origin = expected_type.__origin__
            if origin is Union:
                return any(
                    self._check_type(value, t)
                    for t in expected_type.__args__
                )
            elif origin is list:
                return isinstance(value, list)
            elif origin is dict:
                return isinstance(value, dict)
        
        return isinstance(value, expected_type)
    
    def _is_optional(self, type_hint: type) -> bool:
        """
        Optional型かチェック
        
        Args:
            type_hint: 型ヒント
            
        Returns:
            Optional型の場合True
        """
        if hasattr(type_hint, '__origin__') and type_hint.__origin__ is Union:
            return type(None) in type_hint.__args__
        return False


# プリセットバリデーター

def create_japanese_phone_validator() -> BaseValidator:
    """日本の電話番号バリデーターを作成"""
    from .custom import PhoneValidator
    return PhoneValidator(region='JP', allowed_regions=['JP'])


def create_japanese_postal_code_validator() -> BaseValidator:
    """日本の郵便番号バリデーターを作成"""
    from .custom import RegexValidator
    return RegexValidator(
        pattern=r'^\d{3}-?\d{4}$',
        error_message="有効な郵便番号を入力してください（例: 123-4567）"
    )


def create_password_validator(
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = True
) -> BaseValidator:
    """
    パスワードバリデーターを作成
    
    Args:
        min_length: 最小長
        require_uppercase: 大文字必須
        require_lowercase: 小文字必須
        require_digit: 数字必須
        require_special: 特殊文字必須
        
    Returns:
        パスワードバリデーター
    """
    validators = []
    
    from .custom import LengthValidator, RegexValidator
    
    # 長さチェック
    validators.append(
        LengthValidator(min_length=min_length)
    )
    
    # 大文字チェック
    if require_uppercase:
        validators.append(
            RegexValidator(
                pattern=r'[A-Z]',
                error_message="大文字を含む必要があります"
            )
        )
    
    # 小文字チェック
    if require_lowercase:
        validators.append(
            RegexValidator(
                pattern=r'[a-z]',
                error_message="小文字を含む必要があります"
            )
        )
    
    # 数字チェック
    if require_digit:
        validators.append(
            RegexValidator(
                pattern=r'\d',
                error_message="数字を含む必要があります"
            )
        )
    
    # 特殊文字チェック
    if require_special:
        validators.append(
            RegexValidator(
                pattern=r'[!@#$%^&*(),.?":{}|<>]',
                error_message="特殊文字を含む必要があります"
            )
        )
    
    return AllValidator(validators)