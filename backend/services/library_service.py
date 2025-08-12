"""
ライブラリ管理サービス
library_id/filename ベースの設計

仕様書準拠：
- ライブラリ = ドキュメントコレクション
- 対応形式: PDF, TXT, DOCX, XLSX, PPTX等
- エンベディング連携
"""

import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from pathlib import Path

# ストレージサービスとKVMサービスを使用
from services.storage_service import storage_service
from services.kvm_service import kvm_service


class LibraryService:
    """
    ライブラリ管理サービス
    
    データ構造:
    - KVM: ライブラリメタデータ、ファイル情報
    - BlobStorage/S3: 実際のファイル
    - VectorDB: エンベディング（将来実装）
    """
    
    @staticmethod
    async def create_library(
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        新規ライブラリを作成
        
        Args:
            name: ライブラリ名
            description: 説明
            metadata: メタデータ
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            作成されたライブラリ情報
        """
        # ライブラリIDを生成
        library_id = f"lib_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        # KVMにライブラリメタデータを保存
        library_item = {
            'PK': f"TENANT#{tenant_id}#USER#{user_id}",
            'SK': f"LIBRARY#{library_id}",
            'library_id': library_id,
            'name': name,
            'description': description,
            'file_count': 0,
            'total_size': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'metadata': metadata or {},
            'embedding_status': 'idle',  # idle, processing, completed, failed
            'vector_count': 0
        }
        
        await kvm_service.put_item(library_item)
        
        return {
            'id': library_id,
            'name': name,
            'description': description,
            'file_count': 0,
            'total_size': 0,
            'created_at': library_item['created_at'],
            'updated_at': library_item['updated_at'],
            'metadata': metadata or {}
        }
    
    @staticmethod
    async def get_libraries(
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> List[Dict[str, Any]]:
        """
        ライブラリ一覧を取得
        
        Args:
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            ライブラリリスト
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk_prefix = "LIBRARY#"
        
        items = await kvm_service.query(
            pk=pk,
            sk_prefix=sk_prefix,
            page_size=100
        )
        
        libraries = []
        for item in items:
            libraries.append({
                'id': item.get('library_id'),
                'name': item.get('name'),
                'description': item.get('description', ''),
                'file_count': item.get('file_count', 0),
                'total_size': item.get('total_size', 0),
                'created_at': item.get('created_at'),
                'updated_at': item.get('updated_at'),
                'embedding_status': item.get('embedding_status', 'idle'),
                'vector_count': item.get('vector_count', 0)
            })
        
        return libraries
    
    @staticmethod
    async def get_library(
        library_id: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Optional[Dict[str, Any]]:
        """
        ライブラリ詳細を取得
        
        Args:
            library_id: ライブラリID
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            ライブラリ詳細（ファイル一覧含む）
        """
        # ライブラリメタデータを取得
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk = f"LIBRARY#{library_id}"
        
        library_item = await kvm_service.get_item(pk, sk)
        if not library_item:
            return None
        
        # ファイル一覧を取得
        file_sk_prefix = f"LIBRARY#{library_id}#FILE#"
        file_items = await kvm_service.query(
            pk=pk,
            sk_prefix=file_sk_prefix,
            page_size=100
        )
        
        files = []
        for file_item in file_items:
            files.append({
                'name': file_item.get('filename'),
                'size': file_item.get('size', 0),
                'content_type': file_item.get('content_type'),
                'uploaded_at': file_item.get('uploaded_at'),
                'embedding_status': file_item.get('embedding_status', 'pending'),
                'chunk_count': file_item.get('chunk_count', 0)
            })
        
        return {
            'id': library_id,
            'name': library_item.get('name'),
            'description': library_item.get('description', ''),
            'files': files,
            'file_count': library_item.get('file_count', 0),
            'total_size': library_item.get('total_size', 0),
            'created_at': library_item.get('created_at'),
            'updated_at': library_item.get('updated_at'),
            'metadata': library_item.get('metadata', {}),
            'embedding_status': library_item.get('embedding_status', 'idle'),
            'vector_count': library_item.get('vector_count', 0)
        }
    
    @staticmethod
    async def update_library(
        library_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Optional[Dict[str, Any]]:
        """
        ライブラリ情報を更新
        
        Args:
            library_id: ライブラリID
            name: 新しい名前
            description: 新しい説明
            metadata: 新しいメタデータ
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            更新されたライブラリ情報
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        sk = f"LIBRARY#{library_id}"
        
        updates = {
            'updated_at': datetime.utcnow().isoformat()
        }
        
        if name is not None:
            updates['name'] = name
        if description is not None:
            updates['description'] = description
        if metadata is not None:
            updates['metadata'] = metadata
        
        result = await kvm_service.update_item(pk, sk, updates)
        
        if result.get('success'):
            return await LibraryService.get_library(library_id, tenant_id, user_id)
        
        return None
    
    @staticmethod
    async def delete_library(
        library_id: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        ライブラリとその全ファイルを削除
        
        Args:
            library_id: ライブラリID
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            削除結果
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        
        # ファイル一覧を取得して削除
        file_sk_prefix = f"LIBRARY#{library_id}#FILE#"
        file_items = await kvm_service.query(
            pk=pk,
            sk_prefix=file_sk_prefix,
            page_size=1000
        )
        
        deleted_files = 0
        for file_item in file_items:
            filename = file_item.get('filename')
            if filename:
                # S3/BlobStorageからファイルを削除
                storage_key = f"{tenant_id}/library/{library_id}/{filename}"
                await storage_service.delete_object(storage_key)
                
                # KVMからファイル情報を削除
                await kvm_service.delete_item(pk, file_item['SK'])
                deleted_files += 1
        
        # ライブラリメタデータを削除
        sk = f"LIBRARY#{library_id}"
        await kvm_service.delete_item(pk, sk)
        
        # エンベディングも削除（将来実装）
        # TODO: vector_db.delete_library_embeddings(library_id)
        
        return {
            'message': 'Library deleted successfully',
            'deleted_files': deleted_files
        }
    
    @staticmethod
    async def upload_file(
        library_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        ライブラリにファイルをアップロード
        
        Args:
            library_id: ライブラリID
            filename: ファイル名
            content: ファイル内容
            content_type: コンテンツタイプ
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            アップロード結果
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        
        # ライブラリの存在確認
        library_sk = f"LIBRARY#{library_id}"
        library_item = await kvm_service.get_item(pk, library_sk)
        if not library_item:
            raise ValueError(f"Library {library_id} not found")
        
        # ファイルをS3/BlobStorageに保存
        # ファイルIDを生成（ファイル名に依存しない一意のID）
        import uuid
        file_id = str(uuid.uuid4())[:8]
        
        # 拡張子を取得
        file_ext = '.' + filename.split('.')[-1] if '.' in filename else ''
        
        # ストレージキー（日本語を避けて英数字のみ使用）
        storage_filename = f"file_{file_id}{file_ext}"
        storage_key = f"{tenant_id}/library/{library_id}/{storage_filename}"
        
        # デバッグ: コンテンツの型を確認
        print(f"[DEBUG library_service] Saving file: {filename}")
        print(f"[DEBUG library_service] Content type: {content_type}")
        print(f"[DEBUG library_service] Content is bytes: {isinstance(content, bytes)}")
        print(f"[DEBUG library_service] Content size: {len(content)}")
        
        await storage_service.put_object(
            key=storage_key,
            content=content,  # バイナリのまま渡す（storage_serviceが処理）
            metadata={
                'library_id': library_id,
                'content_type': content_type,
                'uploaded_by': user_id
            },
            content_type=content_type  # コンテンツタイプも渡す
        )
        
        # KVMにファイル情報を保存
        file_size = len(content)
        file_item = {
            'PK': pk,
            'SK': f"LIBRARY#{library_id}#FILE#{filename}",  # SKは元のファイル名を使用
            'library_id': library_id,
            'filename': filename,  # 元のファイル名を保持
            'storage_filename': storage_filename,  # ストレージ用のファイル名
            'file_id': file_id,  # ファイルID
            'size': file_size,
            'content_type': content_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'storage_key': storage_key,
            'embedding_status': 'pending',  # エンベディング待ち
            'chunk_count': 0
        }
        await kvm_service.put_item(file_item)
        
        # ライブラリのファイル数とサイズを更新
        updates = {
            'file_count': library_item.get('file_count', 0) + 1,
            'total_size': library_item.get('total_size', 0) + file_size,
            'updated_at': datetime.utcnow().isoformat()
        }
        await kvm_service.update_item(pk, library_sk, updates)
        
        # 自動エンベディング開始（非同期タスクとして）
        # TODO: asyncio.create_task(start_embedding(library_id, filename))
        
        return {
            'filename': filename,
            'size': file_size,
            'content_type': content_type,
            'uploaded_at': file_item['uploaded_at'],
            'library_id': library_id,
            'embedding_status': 'pending'
        }
    
    @staticmethod
    async def delete_file(
        library_id: str,
        filename: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        ライブラリからファイルを削除
        
        Args:
            library_id: ライブラリID
            filename: ファイル名
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            削除結果
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        
        # ファイル情報を取得
        file_sk = f"LIBRARY#{library_id}#FILE#{filename}"
        file_item = await kvm_service.get_item(pk, file_sk)
        if not file_item:
            raise ValueError(f"File {filename} not found in library {library_id}")
        
        # S3/BlobStorageからファイルを削除
        storage_key = file_item.get('storage_key')
        if not storage_key:
            raise ValueError(f"Storage key not found for file {filename}")
        await storage_service.delete_object(storage_key)
        
        # KVMからファイル情報を削除
        await kvm_service.delete_item(pk, file_sk)
        
        # ライブラリのファイル数とサイズを更新
        library_sk = f"LIBRARY#{library_id}"
        library_item = await kvm_service.get_item(pk, library_sk)
        if library_item:
            updates = {
                'file_count': max(0, library_item.get('file_count', 1) - 1),
                'total_size': max(0, library_item.get('total_size', 0) - file_item.get('size', 0)),
                'updated_at': datetime.utcnow().isoformat()
            }
            await kvm_service.update_item(pk, library_sk, updates)
        
        # エンベディングも削除（将来実装）
        # TODO: vector_db.delete_file_embeddings(library_id, filename)
        
        return {
            'message': 'File deleted successfully',
            'filename': filename
        }
    
    @staticmethod
    async def get_file(
        library_id: str,
        filename: str,
        tenant_id: str = "default_tenant",
        user_id: str = "default_user"
    ) -> Optional[Dict[str, Any]]:
        """
        ファイルをダウンロード
        
        Args:
            library_id: ライブラリID
            filename: ファイル名
            tenant_id: テナントID
            user_id: ユーザーID
            
        Returns:
            ファイル内容とメタデータ
        """
        pk = f"TENANT#{tenant_id}#USER#{user_id}"
        
        # ファイル情報を取得
        file_sk = f"LIBRARY#{library_id}#FILE#{filename}"
        file_item = await kvm_service.get_item(pk, file_sk)
        if not file_item:
            return None
        
        # S3/BlobStorageからファイルを取得
        # ストレージキーを使用（メタデータに保存されている）
        storage_key = file_item.get('storage_key')
        if not storage_key:
            raise ValueError(f"Storage key not found for file {filename}")
        
        # content_typeを確認してバイナリかテキストか判断
        content_type = file_item.get('content_type', '')
        is_binary = not content_type.startswith('text/')
        
        content = await storage_service.get_object(storage_key, return_bytes=is_binary)
        
        if content:
            return {
                'filename': filename,
                'content': content,
                'content_type': content_type,
                'size': file_item.get('size'),
                'uploaded_at': file_item.get('uploaded_at')
            }
        
        return None


# シングルトンインスタンス
library_service = LibraryService()