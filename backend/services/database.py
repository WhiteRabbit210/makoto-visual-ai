from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
import os
from pathlib import Path

# データベースディレクトリの作成
db_dir = Path("./data")
db_dir.mkdir(exist_ok=True)

# データベースファイルのパス
CHAT_DB_PATH = db_dir / "chats.json"
LIBRARY_DB_PATH = db_dir / "library.json"
TASK_DB_PATH = db_dir / "tasks.json"
SETTINGS_DB_PATH = db_dir / "settings.json"

# TinyDBインスタンスの作成（キャッシング付き）
chat_db = TinyDB(CHAT_DB_PATH, storage=CachingMiddleware(JSONStorage))
library_db = TinyDB(LIBRARY_DB_PATH, storage=CachingMiddleware(JSONStorage))
task_db = TinyDB(TASK_DB_PATH, storage=CachingMiddleware(JSONStorage))
settings_db = TinyDB(SETTINGS_DB_PATH, storage=CachingMiddleware(JSONStorage))

# テーブルの取得
chats_table = chat_db.table('chats')
messages_table = chat_db.table('messages')
library_items_table = library_db.table('items')
tasks_table = task_db.table('tasks')
categories_table = task_db.table('categories')
task_templates_table = task_db.table('task_templates')
settings_table = settings_db.table('settings')

# Query オブジェクト
ChatQuery = Query()
MessageQuery = Query()
LibraryQuery = Query()
TaskQuery = Query()
SettingsQuery = Query()