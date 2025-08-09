"""
バリデーターモジュールのテスト
"""

import pytest
from datetime import datetime, timedelta
from makoto_common.validators.custom import (
    EmailValidator, PhoneValidator, URLValidator, UUIDValidator,
    DateTimeValidator, JSONValidator, RegexValidator,
    LengthValidator, RangeValidator, ChoiceValidator
)
from makoto_common.validators.composite import (
    AllValidator, AnyValidator, ConditionalValidator,
    FieldValidator, create_password_validator
)
from makoto_common.errors import ValidationError


class TestEmailValidator:
    """EmailValidatorのテスト"""
    
    def test_valid_email(self):
        """有効なメールアドレステスト"""
        validator = EmailValidator()
        assert validator.validate('test@example.com')
        assert validator.validate('user.name+tag@example.co.jp')
    
    def test_invalid_email(self):
        """無効なメールアドレステスト"""
        validator = EmailValidator()
        
        with pytest.raises(ValidationError):
            validator.validate('invalid-email')
        
        with pytest.raises(ValidationError):
            validator.validate('@example.com')
    
    def test_whitelist_domains(self):
        """ドメインホワイトリストテスト"""
        validator = EmailValidator(whitelist_domains=['example.com', 'test.com'])
        
        assert validator.validate('user@example.com')
        assert validator.validate('user@test.com')
        
        with pytest.raises(ValidationError):
            validator.validate('user@other.com')
    
    def test_blacklist_domains(self):
        """ドメインブラックリストテスト"""
        validator = EmailValidator(blacklist_domains=['spam.com'])
        
        assert validator.validate('user@example.com')
        
        with pytest.raises(ValidationError):
            validator.validate('user@spam.com')


class TestPhoneValidator:
    """PhoneValidatorのテスト"""
    
    def test_valid_japanese_phone(self):
        """有効な日本の電話番号テスト"""
        validator = PhoneValidator(region='JP')
        
        assert validator.validate('+81-3-1234-5678')
        assert validator.validate('090-1234-5678')
        assert validator.validate('03-1234-5678')
    
    def test_invalid_phone(self):
        """無効な電話番号テスト"""
        validator = PhoneValidator(region='JP')
        
        with pytest.raises(ValidationError):
            validator.validate('123456')
        
        with pytest.raises(ValidationError):
            validator.validate('invalid-phone')


class TestURLValidator:
    """URLValidatorのテスト"""
    
    def test_valid_url(self):
        """有効なURLテスト"""
        validator = URLValidator()
        
        assert validator.validate('http://example.com')
        assert validator.validate('https://example.com/path?query=value')
        assert validator.validate('https://sub.example.co.jp:8080/path')
    
    def test_invalid_url(self):
        """無効なURLテスト"""
        validator = URLValidator()
        
        with pytest.raises(ValidationError):
            validator.validate('not-a-url')
        
        with pytest.raises(ValidationError):
            validator.validate('ftp://example.com')  # デフォルトではhttpとhttpsのみ
    
    def test_custom_schemes(self):
        """カスタムスキームテスト"""
        validator = URLValidator(schemes=['http', 'https', 'ftp'])
        
        assert validator.validate('ftp://example.com')


class TestUUIDValidator:
    """UUIDValidatorのテスト"""
    
    def test_valid_uuid(self):
        """有効なUUIDテスト"""
        validator = UUIDValidator()
        
        assert validator.validate('550e8400-e29b-41d4-a716-446655440000')
        assert validator.validate('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    
    def test_invalid_uuid(self):
        """無効なUUIDテスト"""
        validator = UUIDValidator()
        
        with pytest.raises(ValidationError):
            validator.validate('not-a-uuid')
        
        with pytest.raises(ValidationError):
            validator.validate('550e8400-e29b-41d4-a716')


class TestDateTimeValidator:
    """DateTimeValidatorのテスト"""
    
    def test_valid_datetime(self):
        """有効な日時テスト"""
        validator = DateTimeValidator()
        
        assert validator.validate(datetime.now())
        assert validator.validate('2024-01-01 12:00:00')
    
    def test_min_max_datetime(self):
        """最小最大日時テスト"""
        min_date = datetime(2024, 1, 1)
        max_date = datetime(2024, 12, 31)
        validator = DateTimeValidator(min_value=min_date, max_value=max_date)
        
        assert validator.validate(datetime(2024, 6, 15))
        
        with pytest.raises(ValidationError):
            validator.validate(datetime(2023, 12, 31))
        
        with pytest.raises(ValidationError):
            validator.validate(datetime(2025, 1, 1))


class TestJSONValidator:
    """JSONValidatorのテスト"""
    
    def test_valid_json(self):
        """有効なJSONテスト"""
        validator = JSONValidator()
        
        assert validator.validate('{"key": "value"}')
        assert validator.validate({'key': 'value'})
    
    def test_invalid_json(self):
        """無効なJSONテスト"""
        validator = JSONValidator()
        
        with pytest.raises(ValidationError):
            validator.validate('{invalid json}')
    
    def test_json_schema(self):
        """JSONスキーマ検証テスト"""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'number'}
            },
            'required': ['name']
        }
        validator = JSONValidator(schema=schema)
        
        assert validator.validate({'name': 'John', 'age': 30})
        
        with pytest.raises(ValidationError):
            validator.validate({'age': 30})  # nameが必須


class TestRegexValidator:
    """RegexValidatorのテスト"""
    
    def test_pattern_match(self):
        """パターンマッチテスト"""
        validator = RegexValidator(r'^\d{3}-\d{4}$')
        
        assert validator.validate('123-4567')
        
        with pytest.raises(ValidationError):
            validator.validate('1234567')
    
    def test_inverse_match(self):
        """逆マッチテスト"""
        validator = RegexValidator(r'\d+', inverse=True)
        
        assert validator.validate('abc')
        
        with pytest.raises(ValidationError):
            validator.validate('123')


class TestLengthValidator:
    """LengthValidatorのテスト"""
    
    def test_min_max_length(self):
        """最小最大長テスト"""
        validator = LengthValidator(min_length=3, max_length=10)
        
        assert validator.validate('test')
        assert validator.validate('1234567890')
        
        with pytest.raises(ValidationError):
            validator.validate('ab')
        
        with pytest.raises(ValidationError):
            validator.validate('12345678901')
    
    def test_exact_length(self):
        """正確な長さテスト"""
        validator = LengthValidator(exact_length=5)
        
        assert validator.validate('12345')
        
        with pytest.raises(ValidationError):
            validator.validate('1234')


class TestRangeValidator:
    """RangeValidatorのテスト"""
    
    def test_number_range(self):
        """数値範囲テスト"""
        validator = RangeValidator(min_value=0, max_value=100)
        
        assert validator.validate(50)
        assert validator.validate('50')
        
        with pytest.raises(ValidationError):
            validator.validate(-1)
        
        with pytest.raises(ValidationError):
            validator.validate(101)


class TestChoiceValidator:
    """ChoiceValidatorのテスト"""
    
    def test_valid_choice(self):
        """有効な選択肢テスト"""
        validator = ChoiceValidator(['red', 'green', 'blue'])
        
        assert validator.validate('red')
        assert validator.validate('blue')
        
        with pytest.raises(ValidationError):
            validator.validate('yellow')


class TestCompositeValidators:
    """複合バリデーターのテスト"""
    
    def test_all_validator(self):
        """AllValidatorテスト"""
        validator = AllValidator([
            LengthValidator(min_length=5),
            RegexValidator(r'^[a-z]+$')
        ])
        
        assert validator.validate('hello')
        
        with pytest.raises(ValidationError):
            validator.validate('hi')  # 長さ不足
        
        with pytest.raises(ValidationError):
            validator.validate('HELLO')  # 大文字
    
    def test_any_validator(self):
        """AnyValidatorテスト"""
        validator = AnyValidator([
            EmailValidator(),
            PhoneValidator(region='JP')
        ])
        
        assert validator.validate('test@example.com')
        assert validator.validate('090-1234-5678')
        
        with pytest.raises(ValidationError):
            validator.validate('invalid')
    
    def test_conditional_validator(self):
        """ConditionalValidatorテスト"""
        def is_email(value):
            return '@' in str(value)
        
        validator = ConditionalValidator(
            condition=is_email,
            validator=EmailValidator(),
            else_validator=PhoneValidator(region='JP')
        )
        
        assert validator.validate('test@example.com')
        assert validator.validate('090-1234-5678')
    
    def test_password_validator(self):
        """パスワードバリデーターテスト"""
        validator = create_password_validator(
            min_length=8,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
            require_special=True
        )
        
        assert validator.validate('Abc123!@#')
        
        with pytest.raises(ValidationError):
            validator.validate('abc123')  # 大文字と特殊文字なし