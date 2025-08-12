from datetime import datetime
import uuid
from typing import List, Optional
from services.database import library_items_table, LibraryQuery

class LibraryService:
    @staticmethod
    def initialize_sample_data():
        """サンプルデータの初期化"""
        if len(library_items_table.all()) == 0:
            # ルートフォルダ
            root_folder = {
                'id': 'root',
                'name': '全ライブラリ',
                'type': 'folder',
                'parent_id': None,
                'size': 0,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'path': '/'
            }
            library_items_table.insert(root_folder)
            
            # サンプルフォルダ
            sample_folders = [
                {'name': 'MAKOTO操作説明', 'parent_id': 'root'},
                {'name': '視定集', 'parent_id': 'root'},
                {'name': 'テスト操作説明_PDF', 'parent_id': 'root'},
                {'name': '新規ライブラリ', 'parent_id': 'root'}
            ]
            
            for folder_data in sample_folders:
                folder_id = str(uuid.uuid4())
                folder = {
                    'id': folder_id,
                    'name': folder_data['name'],
                    'type': 'folder',
                    'parent_id': folder_data['parent_id'],
                    'size': 0,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'path': f"/{folder_data['name']}"
                }
                library_items_table.insert(folder)
                
                # サンプルファイルを追加
                if folder_data['name'] == 'MAKOTO操作説明':
                    for i in range(1, 4):
                        file_id = str(uuid.uuid4())
                        file_item = {
                            'id': file_id,
                            'name': f'操作説明_0{i}.pdf',
                            'type': 'file',
                            'parent_id': folder_id,
                            'size': 1024 * (100 + i * 50),  # Mock size
                            'created_at': datetime.now().isoformat(),
                            'updated_at': datetime.now().isoformat(),
                            'path': f"/{folder_data['name']}/操作説明_0{i}.pdf"
                        }
                        library_items_table.insert(file_item)

    @staticmethod
    def get_items(parent_id: Optional[str] = None):
        """アイテムを取得"""
        if parent_id:
            return library_items_table.search(LibraryQuery.parent_id == parent_id)
        return library_items_table.all()
    
    @staticmethod
    def get_item(item_id: str):
        """特定のアイテムを取得"""
        items = library_items_table.search(LibraryQuery.id == item_id)
        return items[0] if items else None
    
    @staticmethod
    def create_folder(name: str, parent_id: Optional[str] = None):
        """フォルダを作成"""
        folder_id = str(uuid.uuid4())
        parent_path = "/"
        
        if parent_id:
            parent = LibraryService.get_item(parent_id)
            if parent:
                parent_path = parent['path']
        
        folder = {
            'id': folder_id,
            'name': name,
            'type': 'folder',
            'parent_id': parent_id or 'root',
            'size': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'path': f"{parent_path}/{name}".replace("//", "/")
        }
        
        library_items_table.insert(folder)
        return folder
    
    @staticmethod
    def create_file(name: str, size: int, parent_id: Optional[str] = None):
        """ファイルを作成"""
        file_id = str(uuid.uuid4())
        parent_path = "/"
        
        if parent_id:
            parent = LibraryService.get_item(parent_id)
            if parent:
                parent_path = parent['path']
        
        file_item = {
            'id': file_id,
            'name': name,
            'type': 'file',
            'parent_id': parent_id or 'root',
            'size': size,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'path': f"{parent_path}/{name}".replace("//", "/")
        }
        
        library_items_table.insert(file_item)
        return file_item
    
    @staticmethod
    def delete_item(item_id: str):
        """アイテムとその子要素を削除"""
        # 子要素を取得
        children = library_items_table.search(LibraryQuery.parent_id == item_id)
        
        # 再帰的に子要素を削除
        for child in children:
            LibraryService.delete_item(child['id'])
        
        # アイテム自体を削除
        library_items_table.remove(LibraryQuery.id == item_id)