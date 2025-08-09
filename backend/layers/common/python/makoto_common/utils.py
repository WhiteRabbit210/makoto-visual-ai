"""
ユーティリティ関数群
共通で使用される便利な関数を提供
"""

import hashlib
import json
import logging
import re
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from uuid import uuid4

T = TypeVar('T')

# ロガー設定
def get_logger(name: str = "makoto") -> logging.Logger:
    """
    ロガーを取得
    
    Args:
        name: ロガー名
        
    Returns:
        設定済みのロガー
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

# UUID生成
def get_uuid() -> str:
    """
    UUID v4を生成
    
    Returns:
        UUID文字列
    """
    return str(uuid4())

# タイムスタンプ
def get_timestamp() -> datetime:
    """
    現在のUTCタイムスタンプを取得
    
    Returns:
        UTCタイムスタンプ
    """
    return datetime.now(timezone.utc)

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    日時を文字列にフォーマット
    
    Args:
        dt: 日時オブジェクト
        format_str: フォーマット文字列
        
    Returns:
        フォーマット済み文字列
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    文字列を日時オブジェクトに変換
    
    Args:
        date_str: 日時文字列
        format_str: フォーマット文字列
        
    Returns:
        日時オブジェクト
    """
    dt = datetime.strptime(date_str, format_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

# ハッシュ計算
def calculate_hash(data: Union[str, bytes, Dict], algorithm: str = "sha256") -> str:
    """
    データのハッシュ値を計算
    
    Args:
        data: ハッシュ対象データ
        algorithm: ハッシュアルゴリズム
        
    Returns:
        ハッシュ値（16進数文字列）
    """
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data)
    return hash_obj.hexdigest()

# リトライデコレーター
def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    指数バックオフ付きリトライデコレーター
    
    Args:
        max_retries: 最大リトライ回数
        initial_delay: 初期遅延時間（秒）
        backoff_factor: バックオフ係数
        exceptions: リトライ対象の例外
        
    Returns:
        デコレーター関数
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator

# リスト処理
def chunk_list(items: List[T], chunk_size: int) -> List[List[T]]:
    """
    リストを指定サイズのチャンクに分割
    
    Args:
        items: 分割対象リスト
        chunk_size: チャンクサイズ
        
    Returns:
        チャンクのリスト
    """
    if chunk_size <= 0:
        raise ValueError("チャンクサイズは1以上である必要があります")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

# 辞書処理
def merge_dicts(*dicts: Dict[str, Any], deep: bool = False) -> Dict[str, Any]:
    """
    複数の辞書をマージ
    
    Args:
        *dicts: マージする辞書群
        deep: 深いマージを行うか
        
    Returns:
        マージされた辞書
    """
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
            
        if not deep:
            result.update(d)
        else:
            for key, value in d.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dicts(result[key], value, deep=True)
                else:
                    result[key] = value
    
    return result

# 文字列処理
def sanitize_string(
    text: str,
    max_length: Optional[int] = None,
    allowed_chars: Optional[str] = None
) -> str:
    """
    文字列をサニタイズ
    
    Args:
        text: 対象文字列
        max_length: 最大長
        allowed_chars: 許可する文字パターン（正規表現）
        
    Returns:
        サニタイズ済み文字列
    """
    if not text:
        return ""
    
    # 前後の空白を削除
    text = text.strip()
    
    # 許可文字でフィルタリング
    if allowed_chars:
        text = re.sub(f"[^{allowed_chars}]", "", text)
    
    # 最大長で切り詰め
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text

# バリデーション
def validate_email(email: str) -> bool:
    """
    メールアドレスの形式を検証
    
    Args:
        email: メールアドレス
        
    Returns:
        有効な場合True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    電話番号の形式を検証（日本国内）
    
    Args:
        phone: 電話番号
        
    Returns:
        有効な場合True
    """
    # ハイフンあり・なし両方に対応
    pattern = r'^0\d{1,4}-?\d{1,4}-?\d{4}$|^0\d{9,10}$'
    return bool(re.match(pattern, phone))

# レスポンスフォーマット
def format_error_response(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400
) -> Dict[str, Any]:
    """
    エラーレスポンスをフォーマット
    
    Args:
        error_code: エラーコード
        message: エラーメッセージ
        details: 詳細情報
        status_code: HTTPステータスコード
        
    Returns:
        フォーマット済みエラーレスポンス
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "timestamp": get_timestamp().isoformat()
        },
        "status_code": status_code
    }
    
    if details:
        response["error"]["details"] = details
    
    return response

def format_success_response(
    data: Any,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    成功レスポンスをフォーマット
    
    Args:
        data: レスポンスデータ
        message: メッセージ
        metadata: メタデータ
        
    Returns:
        フォーマット済み成功レスポンス
    """
    response = {
        "success": True,
        "data": data,
        "timestamp": get_timestamp().isoformat()
    }
    
    if message:
        response["message"] = message
    
    if metadata:
        response["metadata"] = metadata
    
    return response