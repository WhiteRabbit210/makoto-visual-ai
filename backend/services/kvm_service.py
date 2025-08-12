"""
KVM (Key-Value Management) サービス
DynamoDB/CosmosDBを使用したメタデータ管理

仕様書: /makoto/docs/仕様書/データ保存仕様書.md#kvm連携
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
from abc import ABC, abstractmethod


class KVMServiceBase(ABC):
    """KVMサービスの基底クラス"""
    
    @abstractmethod
    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを保存"""
        pass
    
    @abstractmethod
    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """アイテムを取得"""
        pass
    
    @abstractmethod
    async def query(self, pk: str, sk_prefix: str = None, page_size: int = 100, 
                   scan_forward: bool = False) -> List[Dict[str, Any]]:
        """アイテムをクエリ"""
        pass
    
    @abstractmethod
    async def update_item(self, pk: str, sk: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを更新"""
        pass
    
    @abstractmethod
    async def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        """アイテムを削除"""
        pass


class DynamoDBService(KVMServiceBase):
    """DynamoDB実装"""
    
    def __init__(self):
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.dynamodb = boto3.resource('dynamodb', 
                                          region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-1'))
            self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'makoto-metadata')
            self.table = self.dynamodb.Table(self.table_name)
            self.ClientError = ClientError
        except ImportError:
            raise ImportError("boto3がインストールされていません。pip install boto3を実行してください。")
    
    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを保存"""
        try:
            # 同期処理を非同期で実行
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.table.put_item, {'Item': item})
            return {'success': True, 'response': response}
        except self.ClientError as e:
            return {'success': False, 'error': str(e)}
    
    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """アイテムを取得"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self.table.get_item,
                {'Key': {'PK': pk, 'SK': sk}}
            )
            return response.get('Item')
        except self.ClientError as e:
            print(f"DynamoDB get_item error: {e}")
            return None
    
    async def query(self, pk: str, sk_prefix: str = None, page_size: int = 100, 
                   scan_forward: bool = False) -> List[Dict[str, Any]]:
        """アイテムをクエリ"""
        try:
            from boto3.dynamodb.conditions import Key
            
            key_condition = Key('PK').eq(pk)
            if sk_prefix:
                key_condition = key_condition & Key('SK').begins_with(sk_prefix)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.table.query(
                    KeyConditionExpression=key_condition,
                    ScanIndexForward=scan_forward,
                    Limit=page_size
                )
            )
            return response.get('Items', [])
        except self.ClientError as e:
            print(f"DynamoDB query error: {e}")
            return []
    
    async def update_item(self, pk: str, sk: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを更新（アトミック更新）"""
        try:
            # 更新式を構築
            update_expression_parts = []
            expression_attribute_names = {}
            expression_attribute_values = {}
            
            for key, value in updates.items():
                # DynamoDBの予約語対策
                attr_name = f"#{key}"
                attr_value = f":{key}"
                
                expression_attribute_names[attr_name] = key
                expression_attribute_values[attr_value] = value
                
                if key == 'message_count' and isinstance(value, int):
                    # カウンターのインクリメント
                    update_expression_parts.append(f"{attr_name} = {attr_name} + {attr_value}")
                else:
                    update_expression_parts.append(f"{attr_name} = {attr_value}")
            
            update_expression = "SET " + ", ".join(update_expression_parts)
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.table.update_item(
                    Key={'PK': pk, 'SK': sk},
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=expression_attribute_names,
                    ExpressionAttributeValues=expression_attribute_values,
                    ReturnValues='ALL_NEW'
                )
            )
            return {'success': True, 'item': response.get('Attributes', {})}
        except self.ClientError as e:
            return {'success': False, 'error': str(e)}
    
    async def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        """アイテムを削除"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.table.delete_item,
                {'Key': {'PK': pk, 'SK': sk}}
            )
            return {'success': True, 'response': response}
        except self.ClientError as e:
            return {'success': False, 'error': str(e)}


class CosmosDBService(KVMServiceBase):
    """Azure Cosmos DB実装"""
    
    def __init__(self):
        try:
            from azure.cosmos import CosmosClient, PartitionKey
            from azure.cosmos.exceptions import CosmosResourceNotFoundError
            
            endpoint = os.getenv('COSMOS_ENDPOINT')
            key = os.getenv('COSMOS_KEY')
            database_name = os.getenv('COSMOS_DATABASE_NAME', 'makoto-db')
            container_name = os.getenv('COSMOS_CONTAINER_NAME', 'metadata')
            
            if not endpoint or not key:
                raise ValueError("COSMOS_ENDPOINTとCOSMOS_KEYが設定されていません")
            
            self.client = CosmosClient(endpoint, key)
            self.database = self.client.get_database_client(database_name)
            self.container = self.database.get_container_client(container_name)
            self.CosmosResourceNotFoundError = CosmosResourceNotFoundError
        except ImportError:
            raise ImportError("azure-cosmosがインストールされていません。pip install azure-cosmosを実行してください。")
    
    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを保存"""
        try:
            # idフィールドを追加（CosmosDBの要件）
            item['id'] = f"{item['PK']}#{item['SK']}"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.container.create_item, item)
            return {'success': True, 'response': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """アイテムを取得"""
        try:
            item_id = f"{pk}#{sk}"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.container.read_item,
                item_id, 
                partition_key=pk
            )
            return response
        except self.CosmosResourceNotFoundError:
            return None
        except Exception as e:
            print(f"CosmosDB get_item error: {e}")
            return None
    
    async def query(self, pk: str, sk_prefix: str = None, page_size: int = 100, 
                   scan_forward: bool = False) -> List[Dict[str, Any]]:
        """アイテムをクエリ"""
        try:
            if sk_prefix:
                query = f"SELECT * FROM c WHERE c.PK = @pk AND STARTSWITH(c.SK, @sk_prefix)"
                parameters = [
                    {"name": "@pk", "value": pk},
                    {"name": "@sk_prefix", "value": sk_prefix}
                ]
            else:
                query = f"SELECT * FROM c WHERE c.PK = @pk"
                parameters = [{"name": "@pk", "value": pk}]
            
            # ORDER BY追加
            if not scan_forward:
                query += " ORDER BY c.SK DESC"
            
            loop = asyncio.get_event_loop()
            items = await loop.run_in_executor(
                None,
                lambda: list(self.container.query_items(
                    query=query,
                    parameters=parameters,
                    max_item_count=page_size
                ))
            )
            return items
        except Exception as e:
            print(f"CosmosDB query error: {e}")
            return []
    
    async def update_item(self, pk: str, sk: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを更新"""
        try:
            item_id = f"{pk}#{sk}"
            
            # 既存アイテムを取得
            existing_item = await self.get_item(pk, sk)
            if not existing_item:
                return {'success': False, 'error': 'Item not found'}
            
            # 更新を適用
            for key, value in updates.items():
                if key == 'message_count' and isinstance(value, int):
                    # カウンターのインクリメント
                    existing_item[key] = existing_item.get(key, 0) + value
                else:
                    existing_item[key] = value
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.container.replace_item,
                item_id,
                existing_item
            )
            return {'success': True, 'item': response}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        """アイテムを削除"""
        try:
            item_id = f"{pk}#{sk}"
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.container.delete_item,
                item_id,
                partition_key=pk
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TinyDBKVMService(KVMServiceBase):
    """開発環境用のTinyDB実装（ローカル永続化）"""
    
    def __init__(self):
        from tinydb import TinyDB, Query
        from pathlib import Path
        
        # データディレクトリを作成
        Path("data").mkdir(exist_ok=True)
        
        # TinyDBを初期化
        self.db = TinyDB('data/kvm_tinydb.json')
        self.Query = Query()
    
    async def put_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを保存"""
        # 既存のアイテムを検索
        Query = self.Query
        existing = self.db.search(
            (Query.PK == item['PK']) & (Query.SK == item['SK'])
        )
        
        if existing:
            # 更新
            self.db.update(
                item,
                (Query.PK == item['PK']) & (Query.SK == item['SK'])
            )
        else:
            # 新規作成
            self.db.insert(item)
        
        return {'success': True, 'response': item}
    
    async def get_item(self, pk: str, sk: str) -> Optional[Dict[str, Any]]:
        """アイテムを取得"""
        Query = self.Query
        results = self.db.search(
            (Query.PK == pk) & (Query.SK == sk)
        )
        return results[0] if results else None
    
    async def query(self, pk: str, sk_prefix: str = None, page_size: int = 100, 
                   scan_forward: bool = False) -> List[Dict[str, Any]]:
        """アイテムをクエリ"""
        Query = self.Query
        
        if sk_prefix:
            # SKプレフィックスでフィルタ
            results = self.db.search(
                (Query.PK == pk) & 
                (Query.SK.matches(f'^{sk_prefix}.*'))
            )
        else:
            # PKのみでフィルタ
            results = self.db.search(Query.PK == pk)
        
        # ソート
        results.sort(key=lambda x: x.get('SK', ''), reverse=not scan_forward)
        
        # limit適用
        return results[:page_size]
    
    async def update_item(self, pk: str, sk: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """アイテムを更新"""
        Query = self.Query
        
        # 既存のアイテムを取得
        existing = await self.get_item(pk, sk)
        if not existing:
            return {'success': False, 'error': 'Item not found'}
        
        # 更新を適用
        for update_key, value in updates.items():
            if update_key == 'message_count' and isinstance(value, int):
                # カウンターのインクリメント
                existing[update_key] = existing.get(update_key, 0) + value
            else:
                existing[update_key] = value
        
        # DBを更新
        self.db.update(
            existing,
            (Query.PK == pk) & (Query.SK == sk)
        )
        
        return {'success': True, 'item': existing}
    
    async def delete_item(self, pk: str, sk: str) -> Dict[str, Any]:
        """アイテムを削除"""
        Query = self.Query
        
        # アイテムの存在確認
        if not await self.get_item(pk, sk):
            return {'success': False, 'error': 'Item not found'}
        
        # 削除
        self.db.remove(
            (Query.PK == pk) & (Query.SK == sk)
        )
        
        return {'success': True}


# KVMサービスのシングルトンインスタンス
def get_kvm_service() -> KVMServiceBase:
    """環境変数に基づいてKVMサービスを取得"""
    kvm_type = os.getenv('KVM_TYPE', 'mock').lower()
    
    if kvm_type == 'dynamodb':
        return DynamoDBService()
    elif kvm_type == 'cosmosdb':
        return CosmosDBService()
    else:
        # 開発環境ではTinyDBを使用（永続化）
        return TinyDBKVMService()


# グローバルインスタンス
kvm_service = get_kvm_service()