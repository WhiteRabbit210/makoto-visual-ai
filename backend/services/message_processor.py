# メッセージサイズ処理サービス
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

class MessageProcessor:
    """
    メッセージのサイズに応じた処理を行うサービス
    - 4KB未満: DynamoDBに直接保存
    - 4KB以上: S3に保存してDynamoDBに参照を保存
    - 128KB超: エラー（画像URLは除外）
    """
    
    def __init__(self):
        self.SMALL_THRESHOLD = 4 * 1024  # 4KB
        self.MAX_SIZE = 128 * 1024  # 128KB
        
    def validate_message_size(self, content: str) -> tuple[bool, int, Optional[str]]:
        """
        メッセージサイズを検証
        
        Returns:
            tuple: (有効かどうか, サイズ（バイト）, エラーメッセージ)
        """
        content_size = len(content.encode('utf-8'))
        
        if content_size > self.MAX_SIZE:
            return False, content_size, f"メッセージサイズが上限（128KB）を超えています: {content_size / 1024:.1f}KB"
        
        return True, content_size, None
    
    def should_use_s3(self, content_size: int) -> bool:
        """
        S3を使用すべきかどうか判定
        """
        return content_size >= self.SMALL_THRESHOLD
    
    def prepare_message_for_storage(self, message: Dict[str, Any], content_size: int) -> Dict[str, Any]:
        """
        保存用にメッセージを準備
        """
        message_copy = message.copy()
        
        # サイズ情報を追加
        message_copy['size_bytes'] = content_size
        
        # S3保存の場合はプレビューを準備
        if self.should_use_s3(content_size):
            content = message.get('content', '')
            preview_length = 200
            if len(content) > preview_length:
                message_copy['content_preview'] = content[:preview_length] + '...'
            message_copy['content_type'] = 'large_text'
            message_copy['storage_type'] = 's3'
        else:
            message_copy['content_type'] = 'text'
            message_copy['storage_type'] = 'dynamodb'
        
        return message_copy
    
    def create_s3_key(self, chat_id: str, message_id: str, message_type: str = 'message') -> str:
        """
        S3キーを生成
        """
        # 本番環境ではテナントIDも含める
        # tenant_id = os.getenv('TENANT_ID', 'default')
        # return f"messages/{tenant_id}/{chat_id}/{message_type}-{message_id}.json"
        
        return f"messages/{chat_id}/{message_type}-{message_id}.json"
    
    def create_s3_reference(self, s3_bucket: str, s3_key: str) -> str:
        """
        S3参照URLを生成
        """
        return f"s3://{s3_bucket}/{s3_key}"