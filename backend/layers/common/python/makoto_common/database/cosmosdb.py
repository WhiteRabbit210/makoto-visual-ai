"""
CosmosDBアダプタ
Azure CosmosDB用のデータベース実装
"""

import os
import json
from typing import Any, Dict, List, Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy
import logging

from .interface import (
    DatabaseInterface,
    QueryResult,
    TransactionItem,
    BatchWriteRequest,
    OperationType
)
from ..types.primitives import TenantId

logger = logging.getLogger(__name__)


class CosmosDBAdapter(DatabaseInterface):
    """
    CosmosDBアダプタ
    テナント別のコンテナ分離を実装
    """
    
    def __init__(
        self,
        tenant_id: Optional[TenantId] = None,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        database_name: str = "makoto",
        consistency_level: str = "Session"
    ):
        """
        初期化
        
        Args:
            tenant_id: テナントID
            endpoint: CosmosDBエンドポイントURL
            key: CosmosDBアクセスキー
            database_name: データベース名
            consistency_level: 一貫性レベル
        """
        super().__init__(tenant_id)
        
        # 環境変数または引数から設定を取得
        self.endpoint = endpoint or os.environ.get('COSMOS_ENDPOINT')
        self.key = key or os.environ.get('COSMOS_KEY')
        
        if not self.endpoint or not self.key:
            raise ValueError("CosmosDBのエンドポイントとキーが必要です")
        
        # CosmosClientの初期化
        self.client = CosmosClient(
            self.endpoint,
            self.key,
            consistency_level=consistency_level
        )
        
        # データベースとコンテナの参照を保持
        self.database_name = database_name
        self.database: Optional[DatabaseProxy] = None
        self.containers: Dict[str, ContainerProxy] = {}
        
        # データベースを初期化
        self._init_database()
    
    def _init_database(self):
        """データベースを初期化"""
        try:
            # データベースが存在しない場合は作成
            self.database = self.client.create_database_if_not_exists(
                id=self.database_name
            )
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"CosmosDBデータベース初期化エラー: {e}")
            raise
    
    def _get_container(self, table_name: str) -> ContainerProxy:
        """
        コンテナを取得（キャッシュ付き）
        
        Args:
            table_name: テーブル名（コンテナ名）
            
        Returns:
            コンテナプロキシ
        """
        # テナント固有のコンテナ名
        container_name = self._get_table_name(table_name)
        
        if container_name not in self.containers:
            try:
                # コンテナが存在しない場合はエラー
                # コンテナはcreate_tableで事前に作成する必要がある
                self.containers[container_name] = self.database.get_container_client(
                    container_name
                )
            except exceptions.CosmosResourceNotFoundError:
                logger.error(f"コンテナが存在しません: {container_name}")
                raise
        
        return self.containers[container_name]
    
    def _convert_dynamodb_to_cosmos_query(
        self,
        key_condition: str,
        expression_values: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        DynamoDB式のクエリをCosmosDB用にSQLに変換
        
        Args:
            key_condition: DynamoDB式のキー条件
            expression_values: 値のマッピング
            
        Returns:
            (SQLクエリ, パラメータ)
        """
        # 簡単な変換ロジック
        # 例: "pk = :pk AND sk = :sk" -> "c.pk = @pk AND c.sk = @sk"
        sql_query = key_condition
        params = []
        
        for placeholder, value in expression_values.items():
            if placeholder.startswith(':'):
                param_name = placeholder[1:]
                sql_query = sql_query.replace(placeholder, f"@{param_name}")
                params.append({"name": f"@{param_name}", "value": value})
        
        # tenant_idフィルタを追加
        tenant_filter = f" AND c.tenant_id = @tenant_id"
        params.append({"name": "@tenant_id", "value": self._get_tenant_id()})
        sql_query = f"SELECT * FROM c WHERE {sql_query}{tenant_filter}"
        
        return sql_query, params
    
    async def get_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        consistent_read: bool = False,
        projection_expression: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        アイテム取得
        """
        try:
            container = self._get_container(table_name)
            
            # CosmosDBではIDとパーティションキーが必要
            item_id = key.get('id') or key.get('pk')
            partition_key = key.get('tenant_id') or self._get_tenant_id()
            
            if not item_id:
                raise ValueError("アイテムIDが必要です")
            
            # アイテムを取得
            response = container.read_item(
                item=item_id,
                partition_key=partition_key
            )
            
            # テナントIDの確認
            if response.get('tenant_id') != self._get_tenant_id():
                return None
            
            return response
            
        except exceptions.CosmosResourceNotFoundError:
            return None
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB get_item エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id(),
                    'key': key
                }
            )
            raise
    
    async def put_item(
        self,
        table_name: str,
        item: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        アイテム保存
        """
        try:
            container = self._get_container(table_name)
            
            # テナントIDをアイテムに含める
            item['tenant_id'] = self._get_tenant_id()
            
            # IDがない場合は生成
            if 'id' not in item:
                if 'pk' in item and 'sk' in item:
                    item['id'] = f"{item['pk']}#{item['sk']}"
                elif 'pk' in item:
                    item['id'] = item['pk']
                else:
                    from uuid import uuid4
                    item['id'] = str(uuid4())
            
            # Upsert（存在すれば更新、なければ挿入）
            container.upsert_item(body=item)
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB put_item エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def update_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        update_expression: str,
        expression_values: Dict[str, Any],
        condition_expression: Optional[str] = None,
        return_values: str = "UPDATED_NEW"
    ) -> Dict[str, Any]:
        """
        アイテム更新
        """
        try:
            container = self._get_container(table_name)
            
            # 既存アイテムを取得
            item_id = key.get('id') or key.get('pk')
            partition_key = key.get('tenant_id') or self._get_tenant_id()
            
            existing_item = container.read_item(
                item=item_id,
                partition_key=partition_key
            )
            
            # テナントIDの確認
            if existing_item.get('tenant_id') != self._get_tenant_id():
                raise ValueError("他テナントのアイテムは更新できません")
            
            # 更新式をパースして適用（簡易実装）
            # SET attr = :val のような式を処理
            if "SET" in update_expression:
                updates = update_expression.replace("SET", "").strip()
                for update in updates.split(","):
                    parts = update.strip().split("=")
                    if len(parts) == 2:
                        attr_name = parts[0].strip()
                        value_placeholder = parts[1].strip()
                        if value_placeholder in expression_values:
                            existing_item[attr_name] = expression_values[value_placeholder]
            
            # 更新を保存
            response = container.replace_item(
                item=item_id,
                body=existing_item
            )
            
            return response
            
        except exceptions.CosmosResourceNotFoundError:
            raise ValueError(f"アイテムが存在しません: {key}")
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB update_item エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id(),
                    'key': key
                }
            )
            raise
    
    async def delete_item(
        self,
        table_name: str,
        key: Dict[str, Any],
        condition_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        アイテム削除
        """
        try:
            container = self._get_container(table_name)
            
            item_id = key.get('id') or key.get('pk')
            partition_key = key.get('tenant_id') or self._get_tenant_id()
            
            # テナントIDの確認（削除前に取得）
            existing_item = container.read_item(
                item=item_id,
                partition_key=partition_key
            )
            
            if existing_item.get('tenant_id') != self._get_tenant_id():
                raise ValueError("他テナントのアイテムは削除できません")
            
            # 削除実行
            container.delete_item(
                item=item_id,
                partition_key=partition_key
            )
            
        except exceptions.CosmosResourceNotFoundError:
            # アイテムが存在しない場合は無視
            pass
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB delete_item エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id(),
                    'key': key
                }
            )
            raise
    
    async def query(
        self,
        table_name: str,
        key_condition: str,
        expression_values: Dict[str, Any],
        index_name: Optional[str] = None,
        limit: Optional[int] = None,
        scan_forward: bool = True,
        projection_expression: Optional[str] = None,
        filter_expression: Optional[str] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None,
        consistent_read: bool = False
    ) -> QueryResult:
        """
        クエリ実行
        """
        try:
            container = self._get_container(table_name)
            
            # DynamoDB式をCosmosDB SQLに変換
            sql_query, params = self._convert_dynamodb_to_cosmos_query(
                key_condition,
                expression_values
            )
            
            # フィルタ追加
            if filter_expression:
                sql_query += f" AND ({filter_expression})"
            
            # ソート順
            if not scan_forward:
                sql_query += " ORDER BY c._ts DESC"
            else:
                sql_query += " ORDER BY c._ts ASC"
            
            # クエリ実行
            query_items = list(container.query_items(
                query=sql_query,
                parameters=params,
                max_item_count=limit,
                enable_cross_partition_query=True
            ))
            
            # 結果を構築
            result = QueryResult(
                items=query_items,
                count=len(query_items),
                scanned_count=len(query_items)
            )
            
            # ページネーションの処理（簡易実装）
            if limit and len(query_items) == limit:
                result.last_evaluated_key = {
                    'id': query_items[-1].get('id'),
                    'tenant_id': query_items[-1].get('tenant_id')
                }
            
            return result
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB query エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def scan(
        self,
        table_name: str,
        filter_expression: Optional[str] = None,
        expression_values: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        projection_expression: Optional[str] = None,
        exclusive_start_key: Optional[Dict[str, Any]] = None,
        consistent_read: bool = False,
        index_name: Optional[str] = None
    ) -> QueryResult:
        """
        スキャン実行
        """
        try:
            container = self._get_container(table_name)
            
            # テナントIDでフィルタリング
            sql_query = f"SELECT * FROM c WHERE c.tenant_id = @tenant_id"
            params = [{"name": "@tenant_id", "value": self._get_tenant_id()}]
            
            # 追加フィルタ
            if filter_expression:
                sql_query += f" AND ({filter_expression})"
                # expression_valuesをパラメータに変換
                if expression_values:
                    for placeholder, value in expression_values.items():
                        if placeholder.startswith(':'):
                            param_name = placeholder[1:]
                            params.append({"name": f"@{param_name}", "value": value})
            
            # スキャン実行
            items = list(container.query_items(
                query=sql_query,
                parameters=params,
                max_item_count=limit,
                enable_cross_partition_query=True
            ))
            
            return QueryResult(
                items=items,
                count=len(items),
                scanned_count=len(items)
            )
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB scan エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def batch_write(
        self,
        requests: List[BatchWriteRequest]
    ) -> Dict[str, Any]:
        """
        バッチ書き込み
        CosmosDBはTransactional Batchをサポート
        """
        unprocessed_items = {}
        tenant_id = self._get_tenant_id()
        
        for request in requests:
            try:
                container = self._get_container(request.table_name)
                
                # PUTリクエスト
                for item in request.put_requests:
                    item['tenant_id'] = tenant_id
                    if 'id' not in item:
                        from uuid import uuid4
                        item['id'] = str(uuid4())
                    
                    try:
                        container.upsert_item(body=item)
                    except exceptions.CosmosHttpResponseError as e:
                        # 失敗したアイテムを記録
                        if request.table_name not in unprocessed_items:
                            unprocessed_items[request.table_name] = []
                        unprocessed_items[request.table_name].append(
                            {'PutRequest': {'Item': item}}
                        )
                        logger.error(f"バッチPUT失敗: {e}")
                
                # DELETEリクエスト
                for key in request.delete_requests:
                    try:
                        item_id = key.get('id') or key.get('pk')
                        partition_key = key.get('tenant_id') or tenant_id
                        
                        container.delete_item(
                            item=item_id,
                            partition_key=partition_key
                        )
                    except exceptions.CosmosHttpResponseError as e:
                        # 失敗したアイテムを記録
                        if request.table_name not in unprocessed_items:
                            unprocessed_items[request.table_name] = []
                        unprocessed_items[request.table_name].append(
                            {'DeleteRequest': {'Key': key}}
                        )
                        logger.error(f"バッチDELETE失敗: {e}")
                        
            except Exception as e:
                logger.error(
                    f"CosmosDB batch_write エラー: {e}",
                    extra={'tenant_id': tenant_id}
                )
        
        return unprocessed_items
    
    async def batch_get(
        self,
        table_name: str,
        keys: List[Dict[str, Any]],
        projection_expression: Optional[str] = None,
        consistent_read: bool = False
    ) -> List[Dict[str, Any]]:
        """
        バッチ読み込み
        """
        try:
            container = self._get_container(table_name)
            tenant_id = self._get_tenant_id()
            items = []
            
            for key in keys:
                try:
                    item_id = key.get('id') or key.get('pk')
                    partition_key = key.get('tenant_id') or tenant_id
                    
                    item = container.read_item(
                        item=item_id,
                        partition_key=partition_key
                    )
                    
                    # テナントIDの確認
                    if item.get('tenant_id') == tenant_id:
                        items.append(item)
                        
                except exceptions.CosmosResourceNotFoundError:
                    # アイテムが存在しない場合はスキップ
                    continue
                except exceptions.CosmosHttpResponseError as e:
                    logger.error(f"バッチGETアイテム取得失敗: {e}")
                    continue
            
            return items
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB batch_get エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def transaction_write(
        self,
        transactions: List[TransactionItem]
    ) -> None:
        """
        トランザクション書き込み
        CosmosDBはTransactional Batchを使用
        """
        # CosmosDBはDynamoDBのようなクロスコンテナトランザクションを
        # サポートしていないため、各操作を順次実行
        # エラーが発生した場合は全体をロールバックする必要がある
        
        tenant_id = self._get_tenant_id()
        completed_operations = []
        
        try:
            for item in transactions:
                container = self._get_container(item.table_name)
                
                if item.operation == OperationType.PUT:
                    if item.item:
                        item.item['tenant_id'] = tenant_id
                        if 'id' not in item.item:
                            from uuid import uuid4
                            item.item['id'] = str(uuid4())
                        container.upsert_item(body=item.item)
                        completed_operations.append((item, 'put'))
                        
                elif item.operation == OperationType.UPDATE:
                    # 更新操作
                    existing_item = container.read_item(
                        item=item.key.get('id'),
                        partition_key=tenant_id
                    )
                    # 更新を適用（簡易実装）
                    # 実際にはupdate_expressionをパースして適用
                    container.replace_item(
                        item=item.key.get('id'),
                        body=existing_item
                    )
                    completed_operations.append((item, 'update'))
                    
                elif item.operation == OperationType.DELETE:
                    container.delete_item(
                        item=item.key.get('id'),
                        partition_key=tenant_id
                    )
                    completed_operations.append((item, 'delete'))
                    
                elif item.operation == OperationType.CONDITION_CHECK:
                    # 条件チェックのみ
                    existing_item = container.read_item(
                        item=item.key.get('id'),
                        partition_key=tenant_id
                    )
                    # 条件を評価（簡易実装）
                    # 実際にはcondition_expressionを評価
                    
        except Exception as e:
            # エラー発生時はロールバックが必要
            # （CosmosDBでは手動で実装が必要）
            logger.error(
                f"CosmosDB transaction_write エラー: {e}",
                extra={'tenant_id': tenant_id}
            )
            # ロールバック処理をここに実装
            raise
    
    async def create_table(
        self,
        table_name: str,
        key_schema: List[Dict[str, str]],
        attribute_definitions: List[Dict[str, str]],
        billing_mode: str = "PAY_PER_REQUEST",
        global_secondary_indexes: Optional[List[Dict[str, Any]]] = None,
        stream_specification: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        テーブル（コンテナ）作成
        """
        try:
            container_name = self._get_table_name(table_name)
            
            # パーティションキーをtenant_idに設定
            partition_key = PartitionKey(path="/tenant_id")
            
            # コンテナを作成
            container = self.database.create_container_if_not_exists(
                id=container_name,
                partition_key=partition_key,
                # スループット設定（PAY_PER_REQUEST相当）
                offer_throughput=None  # サーバーレスモード
            )
            
            # キャッシュに追加
            self.containers[container_name] = container
            
            logger.info(
                f"コンテナ作成完了: {container_name}",
                extra={'tenant_id': self._get_tenant_id()}
            )
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB create_table エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def delete_table(
        self,
        table_name: str
    ) -> None:
        """
        テーブル（コンテナ）削除
        """
        try:
            container_name = self._get_table_name(table_name)
            
            # コンテナを削除
            self.database.delete_container(container_name)
            
            # キャッシュから削除
            if container_name in self.containers:
                del self.containers[container_name]
            
            logger.info(
                f"コンテナ削除完了: {container_name}",
                extra={'tenant_id': self._get_tenant_id()}
            )
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB delete_table エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise
    
    async def describe_table(
        self,
        table_name: str
    ) -> Dict[str, Any]:
        """
        テーブル（コンテナ）情報取得
        """
        try:
            container_name = self._get_table_name(table_name)
            container = self._get_container(table_name)
            
            # コンテナプロパティを取得
            properties = container.read()
            
            return {
                'ContainerName': container_name,
                'PartitionKey': properties.get('partitionKey'),
                'IndexingPolicy': properties.get('indexingPolicy'),
                'UniqueKeyPolicy': properties.get('uniqueKeyPolicy'),
                'ConflictResolutionPolicy': properties.get('conflictResolutionPolicy')
            }
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(
                f"CosmosDB describe_table エラー: {e}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise