import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from contextlib import contextmanager

# ログディレクトリの作成
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# デバッグモードの確認
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


def setup_logger(name: str, log_file: str, level=logging.INFO):
    """
    カスタムロガーのセットアップ
    
    Args:
        name: ロガー名
        log_file: ログファイル名（例: "API.log"）
        level: ログレベル
    
    Returns:
        設定済みのロガー
    """
    logger = logging.getLogger(name)
    
    # 既にハンドラーがある場合はスキップ
    if logger.handlers:
        return logger
    
    # DEBUGモードの場合はDEBUGレベルに設定
    if DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(level)
    
    # ファイルハンドラーの設定（ローテーション付き）
    file_handler = RotatingFileHandler(
        LOG_DIR / log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # フォーマッターの設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # ハンドラーを追加
    logger.addHandler(file_handler)
    
    # DEBUGモードの場合はコンソールにも出力
    if DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


# 各種ロガーの作成
api_logger = setup_logger('API', 'API.log')
chat_logger = setup_logger('CHAT', 'chat.log')
websocket_logger = setup_logger('WEBSOCKET', 'websocket.log')
error_logger = setup_logger('ERROR', 'error.log', logging.ERROR)
performance_logger = setup_logger('PERFORMANCE', 'performance.log')


def log_api_request(endpoint: str, method: str, data: dict = None):
    """APIリクエストのログ"""
    if DEBUG:
        api_logger.debug(f"{method} {endpoint} - Data: {data}")
    else:
        api_logger.info(f"{method} {endpoint}")


def log_api_response(endpoint: str, status_code: int, data: dict = None):
    """APIレスポンスのログ"""
    if DEBUG:
        api_logger.debug(f"Response {endpoint} - Status: {status_code} - Data: {data}")
    else:
        api_logger.info(f"Response {endpoint} - Status: {status_code}")


def log_chat_request(user_message: str, active_modes: list = None):
    """チャットリクエストのログ"""
    chat_logger.info(f"User: {user_message[:100]}... | Modes: {active_modes}")


def log_chat_response(ai_message: str, tokens: dict = None):
    """チャットレスポンスのログ"""
    chat_logger.info(f"AI: {ai_message[:100]}... | Tokens: {tokens}")


def log_error(error_type: str, error_message: str, endpoint: str = None):
    """エラーログ"""
    error_logger.error(f"{error_type} at {endpoint}: {error_message}")


def log_websocket_event(event: str, data: dict = None):
    """WebSocketイベントのログ"""
    websocket_logger.info(f"Event: {event} - Data: {data}")


@contextmanager
def measure_time(operation_name: str, additional_info: dict = None):
    """
    処理時間を計測するコンテキストマネージャー
    
    Args:
        operation_name: 処理名
        additional_info: 追加情報
    """
    start_time = time.time()
    performance_logger.info(f"開始: {operation_name} {additional_info or ''}")
    
    try:
        yield
    finally:
        end_time = time.time()
        duration = end_time - start_time
        performance_logger.info(f"完了: {operation_name} - 実行時間: {duration:.3f}秒 {additional_info or ''}")


def log_performance(operation: str, duration: float, details: dict = None):
    """
    パフォーマンスログの記録
    
    Args:
        operation: 処理名
        duration: 実行時間（秒）
        details: 詳細情報
    """
    details_str = f" - {details}" if details else ""
    performance_logger.info(f"{operation}: {duration:.3f}秒{details_str}")


def log_chat_performance(mode: str, total_time: float, breakdown: dict = None):
    """
    チャット処理のパフォーマンスログ
    
    Args:
        mode: チャットモード（agent, normal）
        total_time: 総実行時間
        breakdown: 処理の内訳
    """
    breakdown_str = ""
    if breakdown:
        breakdown_items = [f"{k}: {v:.3f}s" for k, v in breakdown.items()]
        breakdown_str = f" | 内訳: {', '.join(breakdown_items)}"
    
    performance_logger.info(f"チャット処理 [{mode}] - 総時間: {total_time:.3f}秒{breakdown_str}")