"""
DynamoDBアダプタ
AWS DynamoDB用のデータベース実装
"""

import boto3
from botocore.exceptions import ClientError
from typing import Any, Dict, List, Optional
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


class DynamoDBAdapter(DatabaseInterface):
    """
    DynamoDBアダプタ
    テナント別のテーブル分離を実装
    """
    
    def __init__(
        self,
        tenant_id: Optional[TenantId] = None,
        region_name: str = "ap-northeast-1",
        endpoint_url: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            tenant_id: テナントID
            region_name: AWSリージョン
            endpoint_url: エンドポイントURL（ローカルテスト用）
        """
        super().__init__(tenant_id)
        self.client = boto3.client(
            'dynamodb',
            region_name=region_name,
            endpoint_url=endpoint_url
        )
        self.resource = boto3.resource(
            'dynamodb',
            region_name=region_name,
            endpoint_url=endpoint_url
        )
    
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
            # テナント固有のテーブル名を使用
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            # パラメータ構築
            params = {
                'Key': key,
                'ConsistentRead': consistent_read
            }
            
            if projection_expression:
                params['ProjectionExpression'] = projection_expression
            
            # 取得実行
            response = table.get_item(**params)
            
            return response.get('Item')
            
        except ClientError as e:
            logger.error(
                f"DynamoDB get_item エラー: {e.response['Error']['Message']}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id(),
                    'key': key
                }
            )
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return None
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
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            # テナントIDをアイテムに含める
            item['tenant_id'] = self._get_tenant_id()
            
            params = {'Item': item}
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
                if expression_values:
                    params['ExpressionAttributeValues'] = expression_values
            
            table.put_item(**params)
            
        except ClientError as e:
            logger.error(
                f"DynamoDB put_item エラー: {e.response['Error']['Message']}",
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
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            params = {
                'Key': key,
                'UpdateExpression': update_expression,
                'ExpressionAttributeValues': expression_values,
                'ReturnValues': return_values
            }
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
            
            response = table.update_item(**params)
            
            return response.get('Attributes', {})
            
        except ClientError as e:
            logger.error(
                f"DynamoDB update_item エラー: {e.response['Error']['Message']}",
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
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            params = {'Key': key}
            
            if condition_expression:
                params['ConditionExpression'] = condition_expression
                if expression_values:
                    params['ExpressionAttributeValues'] = expression_values
            
            table.delete_item(**params)
            
        except ClientError as e:
            logger.error(
                f"DynamoDB delete_item エラー: {e.response['Error']['Message']}",
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
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            # テナントIDでフィルタリング
            tenant_filter = "tenant_id = :tenant_id"
            expression_values[':tenant_id'] = self._get_tenant_id()
            
            if filter_expression:
                filter_expression = f"({filter_expression}) AND {tenant_filter}"
            else:
                filter_expression = tenant_filter
            
            params = {
                'KeyConditionExpression': key_condition,
                'ExpressionAttributeValues': expression_values,
                'FilterExpression': filter_expression,
                'ScanIndexForward': scan_forward,
                'ConsistentRead': consistent_read
            }
            
            if index_name:
                params['IndexName'] = index_name
            if limit:
                params['Limit'] = limit
            if projection_expression:
                params['ProjectionExpression'] = projection_expression
            if exclusive_start_key:
                params['ExclusiveStartKey'] = exclusive_start_key
            
            response = table.query(**params)
            
            return QueryResult(
                items=response.get('Items', []),
                last_evaluated_key=response.get('LastEvaluatedKey'),
                count=response.get('Count', 0),
                scanned_count=response.get('ScannedCount', 0),
                consumed_capacity=response.get('ConsumedCapacity')
            )
            
        except ClientError as e:
            logger.error(
                f"DynamoDB query エラー: {e.response['Error']['Message']}",
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
            actual_table_name = self._get_table_name(table_name)
            table = self.resource.Table(actual_table_name)
            
            # テナントIDでフィルタリング
            tenant_filter = "tenant_id = :tenant_id"
            if expression_values is None:
                expression_values = {}
            expression_values[':tenant_id'] = self._get_tenant_id()
            
            if filter_expression:
                filter_expression = f"({filter_expression}) AND {tenant_filter}"
            else:
                filter_expression = tenant_filter
            
            params = {
                'FilterExpression': filter_expression,
                'ExpressionAttributeValues': expression_values,
                'ConsistentRead': consistent_read
            }
            
            if index_name:
                params['IndexName'] = index_name
            if limit:
                params['Limit'] = limit
            if projection_expression:
                params['ProjectionExpression'] = projection_expression
            if exclusive_start_key:
                params['ExclusiveStartKey'] = exclusive_start_key
            
            response = table.scan(**params)
            
            return QueryResult(
                items=response.get('Items', []),
                last_evaluated_key=response.get('LastEvaluatedKey'),
                count=response.get('Count', 0),
                scanned_count=response.get('ScannedCount', 0),
                consumed_capacity=response.get('ConsumedCapacity')
            )
            
        except ClientError as e:
            logger.error(
                f"DynamoDB scan エラー: {e.response['Error']['Message']}",
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
        """
        try:
            tenant_id = self._get_tenant_id()
            request_items = {}
            
            for request in requests:
                actual_table_name = self._get_table_name(request.table_name)
                
                items = []
                # PUTリクエストにテナントIDを追加
                for item in request.put_requests:
                    item['tenant_id'] = tenant_id
                    items.append({'PutRequest': {'Item': item}})
                
                # DELETEリクエスト
                for key in request.delete_requests:
                    items.append({'DeleteRequest': {'Key': key}})
                
                request_items[actual_table_name] = items
            
            response = self.client.batch_write_item(RequestItems=request_items)
            
            return response.get('UnprocessedItems', {})
            
        except ClientError as e:
            logger.error(
                f"DynamoDB batch_write エラー: {e.response['Error']['Message']}",
                extra={'tenant_id': self._get_tenant_id()}
            )
            raise
    
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
            actual_table_name = self._get_table_name(table_name)
            
            request_items = {
                actual_table_name: {
                    'Keys': keys,
                    'ConsistentRead': consistent_read
                }
            }
            
            if projection_expression:
                request_items[actual_table_name]['ProjectionExpression'] = projection_expression
            
            response = self.client.batch_get_item(RequestItems=request_items)
            
            # テナントIDでフィルタリング
            tenant_id = self._get_tenant_id()
            items = response.get('Responses', {}).get(actual_table_name, [])
            
            return [
                item for item in items
                if item.get('tenant_id') == tenant_id
            ]
            
        except ClientError as e:
            logger.error(
                f"DynamoDB batch_get エラー: {e.response['Error']['Message']}",
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
        """
        try:
            tenant_id = self._get_tenant_id()
            transact_items = []
            
            for item in transactions:
                actual_table_name = self._get_table_name(item.table_name)
                
                if item.operation == OperationType.PUT:
                    # テナントIDを追加
                    if item.item:
                        item.item['tenant_id'] = tenant_id
                    
                    transact_item = {
                        'Put': {
                            'TableName': actual_table_name,
                            'Item': item.item
                        }
                    }
                    if item.condition_expression:
                        transact_item['Put']['ConditionExpression'] = item.condition_expression
                        if item.expression_values:
                            transact_item['Put']['ExpressionAttributeValues'] = item.expression_values
                    
                elif item.operation == OperationType.UPDATE:
                    transact_item = {
                        'Update': {
                            'TableName': actual_table_name,
                            'Key': item.key,
                            'UpdateExpression': item.update_expression
                        }
                    }
                    if item.expression_values:
                        transact_item['Update']['ExpressionAttributeValues'] = item.expression_values
                    if item.condition_expression:
                        transact_item['Update']['ConditionExpression'] = item.condition_expression
                    
                elif item.operation == OperationType.DELETE:
                    transact_item = {
                        'Delete': {
                            'TableName': actual_table_name,
                            'Key': item.key
                        }
                    }
                    if item.condition_expression:
                        transact_item['Delete']['ConditionExpression'] = item.condition_expression
                        if item.expression_values:
                            transact_item['Delete']['ExpressionAttributeValues'] = item.expression_values
                    
                elif item.operation == OperationType.CONDITION_CHECK:
                    transact_item = {
                        'ConditionCheck': {
                            'TableName': actual_table_name,
                            'Key': item.key,
                            'ConditionExpression': item.condition_expression
                        }
                    }
                    if item.expression_values:
                        transact_item['ConditionCheck']['ExpressionAttributeValues'] = item.expression_values
                
                transact_items.append(transact_item)
            
            self.client.transact_write_items(TransactItems=transact_items)
            
        except ClientError as e:
            logger.error(
                f"DynamoDB transaction_write エラー: {e.response['Error']['Message']}",
                extra={'tenant_id': self._get_tenant_id()}
            )
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
        テーブル作成
        """
        try:
            actual_table_name = self._get_table_name(table_name)
            
            # テナントID属性を追加
            if not any(attr['AttributeName'] == 'tenant_id' for attr in attribute_definitions):
                attribute_definitions.append({
                    'AttributeName': 'tenant_id',
                    'AttributeType': 'S'
                })
            
            params = {
                'TableName': actual_table_name,
                'KeySchema': key_schema,
                'AttributeDefinitions': attribute_definitions,
                'BillingMode': billing_mode
            }
            
            if global_secondary_indexes:
                # GSIにtenant_idを含める
                for gsi in global_secondary_indexes:
                    if 'tenant_id' not in [key['AttributeName'] for key in gsi['KeySchema']]:
                        gsi['KeySchema'].insert(0, {
                            'AttributeName': 'tenant_id',
                            'KeyType': 'HASH'
                        })
                params['GlobalSecondaryIndexes'] = global_secondary_indexes
            
            if stream_specification:
                params['StreamSpecification'] = stream_specification
            
            self.client.create_table(**params)
            
            # テーブルがアクティブになるまで待機
            waiter = self.client.get_waiter('table_exists')
            waiter.wait(TableName=actual_table_name)
            
            logger.info(
                f"テーブル作成完了: {actual_table_name}",
                extra={'tenant_id': self._get_tenant_id()}
            )
            
        except ClientError as e:
            logger.error(
                f"DynamoDB create_table エラー: {e.response['Error']['Message']}",
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
        テーブル削除
        """
        try:
            actual_table_name = self._get_table_name(table_name)
            
            self.client.delete_table(TableName=actual_table_name)
            
            # テーブルが削除されるまで待機
            waiter = self.client.get_waiter('table_not_exists')
            waiter.wait(TableName=actual_table_name)
            
            logger.info(
                f"テーブル削除完了: {actual_table_name}",
                extra={'tenant_id': self._get_tenant_id()}
            )
            
        except ClientError as e:
            logger.error(
                f"DynamoDB delete_table エラー: {e.response['Error']['Message']}",
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
        テーブル情報取得
        """
        try:
            actual_table_name = self._get_table_name(table_name)
            
            response = self.client.describe_table(TableName=actual_table_name)
            
            return response['Table']
            
        except ClientError as e:
            logger.error(
                f"DynamoDB describe_table エラー: {e.response['Error']['Message']}",
                extra={
                    'table': table_name,
                    'tenant_id': self._get_tenant_id()
                }
            )
            raise