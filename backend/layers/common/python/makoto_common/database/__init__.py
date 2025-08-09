"""
データベース抽象化モジュール
DynamoDBとCosmosDBの統一インターフェースを提供
"""

from .interface import (
    DatabaseInterface,
    QueryResult,
    TransactionItem,
    BatchWriteRequest,
    ConsistencyLevel,
    OperationType
)

from .dynamodb import DynamoDBAdapter
from .cosmosdb import CosmosDBAdapter
from .factory import DatabaseFactory, get_database

__all__ = [
    # インターフェース
    'DatabaseInterface',
    'QueryResult',
    'TransactionItem',
    'BatchWriteRequest',
    'ConsistencyLevel',
    'OperationType',
    
    # 実装
    'DynamoDBAdapter',
    'CosmosDBAdapter',
    
    # ファクトリ
    'DatabaseFactory',
    'get_database'
]