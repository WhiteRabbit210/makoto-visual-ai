# 統一ストレージサービス
import os
import json
from typing import Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from enum import Enum


class StorageType(Enum):
    """ストレージタイプの定義"""
    LOCAL = 'local'
    S3 = 's3'
    AZURE = 'azure'


class StorageService:
    """
    S3、Azure Blob Storage、ローカルストレージを統一的に扱うためのサービス
    環境変数STORAGE_TYPEに応じて適切な実装を使用
    """
    
    def __init__(self):
        # ストレージタイプを環境変数から取得
        storage_type_str = os.getenv('STORAGE_TYPE', 'local').lower()
        
        # ストレージタイプを判定
        if storage_type_str == 's3':
            self.storage_type = StorageType.S3
            self.bucket_name = os.getenv('S3_BUCKET_NAME', 'makoto-messages')
        elif storage_type_str == 'azure':
            self.storage_type = StorageType.AZURE
            self.container_name = os.getenv('AZURE_CONTAINER_NAME', 'makoto-messages')
            self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        else:
            self.storage_type = StorageType.LOCAL
            from services.local_storage_service import local_storage
            self.local_storage = local_storage
    
    async def put_object(self, key: str, content: Union[str, bytes], 
                        metadata: Optional[Dict[str, str]] = None,
                        content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        オブジェクトを保存
        
        Args:
            key: オブジェクトキー
            content: 保存するコンテンツ（文字列またはバイナリ）
            metadata: メタデータ
            content_type: コンテンツタイプ
            
        Returns:
            保存結果
        """
        # バイナリコンテンツの処理
        print(f"[DEBUG storage_service] put_object called")
        print(f"[DEBUG storage_service] Key: {key}")
        print(f"[DEBUG storage_service] Content type param: {content_type}")
        print(f"[DEBUG storage_service] Content is str: {isinstance(content, str)}")
        print(f"[DEBUG storage_service] Content is bytes: {isinstance(content, bytes)}")
        
        if isinstance(content, str):
            body = content.encode('utf-8')
        else:
            body = content
        
        if self.storage_type == StorageType.S3:
            # S3を使用
            import aioboto3
            async with aioboto3.Session().client('s3') as s3:
                response = await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=body,
                    ContentType=content_type or 'application/octet-stream',
                    Metadata=metadata or {}
                )
                return {
                    'success': True,
                    'url': f"s3://{self.bucket_name}/{key}"
                }
        
        elif self.storage_type == StorageType.AZURE:
            # Azure Blob Storageを使用
            from azure.storage.blob.aio import BlobServiceClient
            
            # 接続文字列からBlobServiceClientを作成
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            try:
                # コンテナクライアントを取得
                container_client = blob_service_client.get_container_client(
                    self.container_name
                )
                
                # Blobをアップロード
                blob_client = container_client.get_blob_client(key)
                await blob_client.upload_blob(
                    body,
                    overwrite=True,
                    content_type=content_type or 'application/octet-stream',
                    metadata=metadata
                )
                
                return {
                    'success': True,
                    'url': f"azure://{self.container_name}/{key}"
                }
            finally:
                await blob_service_client.close()
        
        else:
            # ローカルストレージを使用
            # バイナリもテキストもそのまま渡す（local_storage_serviceが処理）
            result = await self.local_storage.put_object(
                key=key,
                body=body,  # バイナリのまま渡す
                metadata=metadata
            )
            return {
                'success': result['success'],
                'url': self.local_storage.create_local_url(key)
            }
    
    async def get_object(self, key: str, return_bytes: bool = False) -> Optional[Union[str, bytes]]:
        """
        オブジェクトを取得
        
        Args:
            key: オブジェクトキー
            return_bytes: バイナリとして返すかどうか
            
        Returns:
            コンテンツ（存在しない場合はNone）
        """
        if self.storage_type == StorageType.S3:
            # S3を使用
            import aioboto3
            try:
                async with aioboto3.Session().client('s3') as s3:
                    response = await s3.get_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    body = await response['Body'].read()
                    
                    if return_bytes:
                        return body
                    else:
                        return body.decode('utf-8')
            except Exception:
                return None
        
        elif self.storage_type == StorageType.AZURE:
            # Azure Blob Storageを使用
            from azure.storage.blob.aio import BlobServiceClient
            
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            try:
                # Blobをダウンロード
                blob_client = blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=key
                )
                
                download_stream = await blob_client.download_blob()
                body = await download_stream.readall()
                
                if return_bytes:
                    return body
                else:
                    return body.decode('utf-8')
            except Exception:
                return None
            finally:
                await blob_service_client.close()
        
        else:
            # ローカルストレージを使用
            result = await self.local_storage.get_object(key=key)
            if result:
                content = result['Body']
                
                # contentがバイナリかテキストかで処理を分ける
                if isinstance(content, bytes):
                    if return_bytes:
                        return content
                    else:
                        return content.decode('utf-8')
                else:
                    if return_bytes:
                        return content.encode('utf-8')
                    else:
                        return content
            return None
    
    async def get_object_from_url(self, url: str, return_bytes: bool = False) -> Optional[Union[str, bytes]]:
        """
        URLからオブジェクトを取得
        
        Args:
            url: S3 URL、Azure URLまたはローカルURL
            return_bytes: バイナリとして返すかどうか
            
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
        elif url.startswith('azure://'):
            # azure://container-name/key/path
            parts = url.replace('azure://', '').split('/', 1)
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
        
        return await self.get_object(key, return_bytes=return_bytes)
    
    def create_url(self, key: str) -> str:
        """
        キーからURLを生成
        
        Args:
            key: オブジェクトキー
            
        Returns:
            URL
        """
        if self.storage_type == StorageType.S3:
            return f"s3://{self.bucket_name}/{key}"
        elif self.storage_type == StorageType.AZURE:
            return f"azure://{self.container_name}/{key}"
        else:
            return self.local_storage.create_local_url(key)

    async def list_objects(self, prefix: str, page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        プレフィックスに一致するオブジェクトをリスト
        
        Args:
            prefix: プレフィックス（例: "user_id/chat_id/2025/08/"）
            page_size: 1ページあたりの件数
            
        Returns:
            オブジェクトリストと継続トークン
        """
        if self.storage_type == StorageType.S3:
            # S3を使用
            import aioboto3
            objects = []
            try:
                async with aioboto3.Session().client('s3') as s3:
                    paginator = s3.get_paginator('list_objects_v2')
                    pagination_config = {'PageSize': 100}
                    if page_size:
                        pagination_config['MaxItems'] = page_size
                    
                    page_iterator = paginator.paginate(
                        Bucket=self.bucket_name,
                        Prefix=prefix,
                        PaginationConfig=pagination_config
                    )
                    
                    async for page in page_iterator:
                        if 'Contents' in page:
                            for obj in page['Contents']:
                                objects.append({
                                    'key': obj['Key'],
                                    'size': obj['Size'],
                                    'last_modified': obj['LastModified'].isoformat() if hasattr(obj['LastModified'], 'isoformat') else str(obj['LastModified'])
                                })
                                if page_size and len(objects) >= page_size:
                                    break
                        if page_size and len(objects) >= page_size:
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
        
        elif self.storage_type == StorageType.AZURE:
            # Azure Blob Storageを使用
            from azure.storage.blob.aio import BlobServiceClient
            
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            objects = []
            try:
                container_client = blob_service_client.get_container_client(
                    self.container_name
                )
                
                # プレフィックスでBlobをリスト
                async for blob in container_client.list_blobs(
                    name_starts_with=prefix
                ):
                    objects.append({
                        'key': blob.name,
                        'size': blob.size,
                        'last_modified': blob.last_modified.isoformat() if blob.last_modified else None
                    })
                    
                    if page_size and len(objects) >= page_size:
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
            finally:
                await blob_service_client.close()
        
        else:
            # ローカルストレージを使用
            result = await self.local_storage.list_objects(prefix=prefix, page_size=page_size)
            return result
    
    async def delete_object(self, key: str) -> Dict[str, Any]:
        """
        オブジェクトを削除
        
        Args:
            key: オブジェクトキー
            
        Returns:
            削除結果
        """
        if self.storage_type == StorageType.S3:
            # S3を使用
            import aioboto3
            try:
                async with aioboto3.Session().client('s3') as s3:
                    await s3.delete_object(
                        Bucket=self.bucket_name,
                        Key=key
                    )
                    return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        elif self.storage_type == StorageType.AZURE:
            # Azure Blob Storageを使用
            from azure.storage.blob.aio import BlobServiceClient
            
            blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            
            try:
                blob_client = blob_service_client.get_blob_client(
                    container=self.container_name,
                    blob=key
                )
                await blob_client.delete_blob()
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}
            finally:
                await blob_service_client.close()
        
        else:
            # ローカルストレージを使用
            # TODO: local_storage_serviceにdelete_objectメソッドを実装
            return {'success': True, 'message': 'Local delete not implemented'}

# シングルトンインスタンス
storage_service = StorageService()