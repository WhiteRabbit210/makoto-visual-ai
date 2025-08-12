# 統一ストレージサービス
import os
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

class StorageService:
    """
    S3とローカルストレージを統一的に扱うためのサービス
    環境変数USE_S3に応じて適切な実装を使用
    """
    
    def __init__(self):
        self.use_s3 = os.getenv('USE_S3', 'false').lower() == 'true'
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'makoto-messages')
        
        if not self.use_s3:
            from services.local_storage_service import local_storage
            self.local_storage = local_storage
    
    async def put_object(self, key: str, content: str, 
                        metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        オブジェクトを保存
        
        Args:
            key: オブジェクトキー
            content: 保存するコンテンツ
            metadata: メタデータ
            
        Returns:
            保存結果
        """
        if self.use_s3:
            # S3を使用（将来実装）
            import aioboto3
            async with aioboto3.Session().client('s3') as s3:
                response = await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=content.encode('utf-8'),
                    ContentType='application/json',
                    Metadata=metadata or {}
                )
                return {
                    'success': True,
                    'url': f"s3://{self.bucket_name}/{key}"
                }
        else:
            # ローカルストレージを使用
            result = await self.local_storage.put_object(
                key=key,
                body=content,
                metadata=metadata
            )
            return {
                'success': result['success'],
                'url': self.local_storage.create_local_url(key)
            }
    
    async def get_object(self, key: str) -> Optional[str]:
        """
        オブジェクトを取得
        
        Args:
            key: オブジェクトキー
            
        Returns:
            コンテンツ（存在しない場合はNone）
        """
        if self.use_s3:
            # S3を使用（将来実装）
            import aioboto3
            try:
                async with aioboto3.Session().client('s3') as s3:
                    response = await s3.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    body = await response['Body'].read()
                    return body.decode('utf-8')
            except Exception:
                return None
        else:
            # ローカルストレージを使用
            result = await self.local_storage.get_object(key=key)
            if result:
                return result['Body']
            return None
    
    async def get_object_from_url(self, url: str) -> Optional[str]:
        """
        URLからオブジェクトを取得
        
        Args:
            url: S3 URLまたはローカルURL
            
        Returns:
            コンテンツ（存在しない場合はNone）
        """
        # URLからキーを抽出
        if url.startswith('s3://'):
            # s3://bucket-name/key/path
            parts = url.replace('s3://', '').split('/', 1)
            if len(parts) > 1:
                key = parts[1]
            else:
                return None
        elif url.startswith('local://'):
            # local://storage/key/path
            key = self.local_storage.parse_local_url(url)
            if not key:
                return None
        else:
            return None
        
        return await self.get_object(key)
    
    def create_url(self, key: str) -> str:
        """
        キーからURLを生成
        
        Args:
            key: オブジェクトキー
            
        Returns:
            URL
        """
        if self.use_s3:
            return f"s3://{self.bucket_name}/{key}"
        else:
            return self.local_storage.create_local_url(key)

    async def list_objects(self, prefix: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        プレフィックスに一致するオブジェクトをリスト
        
        Args:
            prefix: プレフィックス（例: "user_id/chat_id/2025/08/"）
            limit: 取得する最大数
            
        Returns:
            オブジェクトリストと継続トークン
        """
        if self.use_s3:
            # S3を使用
            import aioboto3
            objects = []
            try:
                async with aioboto3.Session().client('s3') as s3:
                    paginator = s3.get_paginator('list_objects_v2')
                    page_iterator = paginator.paginate(
                        Bucket=self.bucket_name,
                        Prefix=prefix,
                        PaginationConfig={
                            'MaxItems': limit if limit else 1000,
                            'PageSize': 100
                        }
                    )
                    
                    async for page in page_iterator:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                objects.append({
                                    'key': obj['Key'],
                                    'size': obj['Size'],
                                    'last_modified': obj['LastModified'].isoformat() if hasattr(obj['LastModified'], 'isoformat') else str(obj['LastModified'])
                                })
                                if limit and len(objects) >= limit:
                                    break
                        if limit and len(objects) >= limit:
                            break
                    
                    return {
                        'success': True,
                        'objects': objects,
                        'count': len(objects)
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'objects': [],
                    'count': 0
                }
        else:
            # ローカルストレージを使用
            result = await self.local_storage.list_objects(prefix=prefix, limit=limit)
            return result

# シングルトンインスタンス
storage_service = StorageService()