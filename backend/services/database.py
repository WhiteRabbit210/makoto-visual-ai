"""
ローカルインデックス管理用データベース

本番データはKVMサービス（DynamoDB/CosmosDB）とBlobStorage/S3に保存されます。
TinyDBはローカル開発時のインデックスキャッシュとして使用します。
"""

from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# ローカルインデックスディレクトリの作成
index_dir = Path("./data/local_index")
index_dir.mkdir(parents=True, exist_ok=True)

# インデックスファイルのパス
CHAT_INDEX_PATH = index_dir / "chat_index.json"
MESSAGE_INDEX_PATH = index_dir / "message_index.json"
LIBRARY_INDEX_PATH = index_dir / "library_index.json"

# TinyDBインスタンス（ローカルインデックス用）
chat_index_db = TinyDB(CHAT_INDEX_PATH, storage=CachingMiddleware(JSONStorage))
message_index_db = TinyDB(MESSAGE_INDEX_PATH, storage=CachingMiddleware(JSONStorage))
library_index_db = TinyDB(LIBRARY_INDEX_PATH, storage=CachingMiddleware(JSONStorage))

# インデックステーブル
chat_index_table = chat_index_db.table('chat_index')
message_index_table = message_index_db.table('message_index')
library_index_table = library_index_db.table('library_index')

# Query オブジェクト
IndexQuery = Query()

class LocalIndexService:
    """ローカルインデックス管理サービス"""
    
    @staticmethod
    def update_chat_index(room_id: str, metadata: Dict[str, Any]):
        """チャットのインデックス更新"""
        chat_index_table.upsert(
            {
                'room_id': room_id,
                'title': metadata.get('title'),
                'updated_at': metadata.get('updated_at'),
                'message_count': metadata.get('message_count', 0),
                'last_accessed': datetime.now().isoformat()
            },
            IndexQuery.room_id == room_id
        )
    
    @staticmethod
    def get_chat_index(room_id: str) -> Optional[Dict[str, Any]]:
        """チャットインデックスの取得"""
        result = chat_index_table.search(IndexQuery.room_id == room_id)
        return result[0] if result else None
    
    @staticmethod
    def update_message_index(room_id: str, message_id: str, storage_path: str):
        """メッセージのストレージパスをインデックスに保存"""
        message_index_table.insert({
            'room_id': room_id,
            'message_id': message_id,
            'storage_path': storage_path,
            'indexed_at': datetime.now().isoformat()
        })
    
    @staticmethod
    def get_message_paths(room_id: str, limit: int = 50) -> List[str]:
        """メッセージのストレージパスを取得"""
        results = message_index_table.search(IndexQuery.room_id == room_id)
        # 最新のものから返す
        sorted_results = sorted(results, key=lambda x: x.get('indexed_at', ''), reverse=True)
        return [r['storage_path'] for r in sorted_results[:limit]]
    
    @staticmethod
    def clear_old_index(days: int = 7):
        """古いインデックスをクリア"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 古いチャットインデックスを削除
        chat_index_table.remove(IndexQuery.last_accessed < cutoff)
        
        # 古いメッセージインデックスを削除
        message_index_table.remove(IndexQuery.indexed_at < cutoff)

# エクスポート
local_index_service = LocalIndexService()