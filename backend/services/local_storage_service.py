# ローカルストレージサービス（S3の代替）
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
import aiofiles
import asyncio

class LocalStorageService:
    """
    S3の代替としてローカルファイルシステムを使用するストレージサービス
    本番環境ではS3を使用するが、開発環境ではローカルストレージを使用
    """
    
    def __init__(self):
        # ストレージのベースディレクトリ
        self.base_dir = Path("./data/local_storage")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_full_path(self, key: str) -> Path:
        """
        S3キーからローカルファイルパスを生成
        """
        # キーの先頭のスラッシュを除去
        key = key.lstrip('/')
        return self.base_dir / key
    
    async def put_object(self, key: str, body, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        オブジェクトを保存（S3のput_objectを模倣）
        
        Args:
            key: オブジェクトキー（S3のキーと同じ形式）
            body: 保存するコンテンツ（文字列またはバイナリ）
            metadata: メタデータ
            
        Returns:
            保存結果
        """
        file_path = self._get_full_path(key)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # バイナリかテキストかを判定
        is_binary = isinstance(body, bytes)
        
        if is_binary:
            # バイナリファイルは直接保存
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(body)
            size = len(body)
        else:
            # テキストファイルはそのまま保存
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(body)
            size = len(body.encode('utf-8'))
        
        # メタデータは無視（KVMで管理されているため）
        # S3/Azureのオブジェクトメタデータは、ローカルストレージでは不要
        
        return {
            "success": True,
            "key": key,
            "size": size,
            "local_path": str(file_path)
        }
    
    async def get_object(self, key: str) -> Optional[Dict[str, Any]]:
        """
        オブジェクトを取得（S3のget_objectを模倣）
        
        Args:
            key: オブジェクトキー
            
        Returns:
            取得したコンテンツとメタデータ
        """
        file_path = self._get_full_path(key)
        
        if not file_path.exists():
            return None
        
        # ファイルの内容を確認してバイナリかテキストか判定
        try:
            # まずテキストとして読み込みを試みる
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            is_binary = False
        except UnicodeDecodeError:
            # テキストとして読めない場合はバイナリ
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            is_binary = True
        
        return {
            "Body": content,
            "Metadata": {},  # ローカルストレージではメタデータなし（KVMで管理）
            "ContentLength": len(content) if is_binary else len(content.encode('utf-8'))
        }
    
    async def delete_object(self, key: str) -> bool:
        """
        オブジェクトを削除（S3のdelete_objectを模倣）
        
        Args:
            key: オブジェクトキー
            
        Returns:
            削除成功かどうか
        """
        file_path = self._get_full_path(key)
        
        if file_path.exists():
            file_path.unlink()
            # 空のディレクトリを削除
            try:
                file_path.parent.rmdir()
            except OSError:
                # ディレクトリが空でない場合は無視
                pass
            return True
        
        return False
    
    async def list_objects(self, prefix: str = "", limit: Optional[int] = None) -> Dict[str, Any]:
        """
        プレフィックスに一致するオブジェクトをリスト（S3のlist_objectsを模倣）
        
        Args:
            prefix: プレフィックス
            limit: 取得する最大数
            
        Returns:
            オブジェクト情報のリスト
        """
        prefix_path = self._get_full_path(prefix)
        objects = []
        
        # ディレクトリが存在しない場合は空のリストを返す
        if not prefix_path.exists():
            # プレフィックスが完全なディレクトリパスでない可能性があるので、親ディレクトリも確認
            parent_dir = prefix_path.parent if not prefix_path.is_dir() else prefix_path
            if parent_dir.exists():
                # 親ディレクトリ内でプレフィックスにマッチするファイルを検索
                for file_path in parent_dir.rglob("*"):
                    if file_path.is_file():
                        key = str(file_path.relative_to(self.base_dir)).replace(os.sep, '/')
                        if key.startswith(prefix):
                            stat = file_path.stat()
                            objects.append({
                                'key': key,
                                'size': stat.st_size,
                                'last_modified': stat.st_mtime
                            })
                            if limit and len(objects) >= limit:
                                break
        else:
            # プレフィックスパスがディレクトリの場合
            if prefix_path.is_dir():
                for file_path in prefix_path.rglob("*"):
                    if file_path.is_file():
                        key = str(file_path.relative_to(self.base_dir)).replace(os.sep, '/')
                        stat = file_path.stat()
                        objects.append({
                            'key': key,
                            'size': stat.st_size,
                            'last_modified': stat.st_mtime
                        })
                        if limit and len(objects) >= limit:
                            break
        
        # 時刻順にソート（新しい順）
        objects.sort(key=lambda x: x['last_modified'], reverse=True)
        
        return {
            'success': True,
            'objects': objects,
            'count': len(objects)
        }
    
    def create_local_url(self, key: str) -> str:
        """
        ローカルストレージURLを生成（S3 URLの代替）
        """
        return f"local://storage/{key}"
    
    def parse_local_url(self, url: str) -> Optional[str]:
        """
        ローカルストレージURLからキーを抽出
        """
        if url.startswith("local://storage/"):
            return url.replace("local://storage/", "")
        elif url.startswith("s3://"):
            # S3 URLの場合はバケット名を除去してキーを返す
            parts = url.replace("s3://", "").split('/', 1)
            if len(parts) > 1:
                return parts[1]
        return None

# シングルトンインスタンス
local_storage = LocalStorageService()