"""
データベース抽象化モジュールのテスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from makoto_common.database.interface import DatabaseInterface, QueryBuilder
from makoto_common.database.dynamodb import DynamoDBAdapter
from makoto_common.database.factory import DatabaseFactory


class TestQueryBuilder:
    """QueryBuilderのテスト"""
    
    def test_filter_single_condition(self):
        """単一条件フィルタテスト"""
        builder = QueryBuilder('users')
        builder.filter('age', '>', 18)
        
        assert len(builder.conditions) == 1
        assert builder.conditions[0] == {
            'field': 'age',
            'operator': '>',
            'value': 18
        }
    
    def test_filter_multiple_conditions(self):
        """複数条件フィルタテスト"""
        builder = QueryBuilder('users')
        builder.filter('age', '>', 18).filter('status', '=', 'active')
        
        assert len(builder.conditions) == 2
    
    def test_sort(self):
        """ソートテスト"""
        builder = QueryBuilder('users')
        builder.sort('created_at', descending=True)
        
        assert builder.sort_key == 'created_at'
        assert builder.sort_descending is True
    
    def test_limit(self):
        """リミットテスト"""
        builder = QueryBuilder('users')
        builder.limit(10)
        
        assert builder.limit_value == 10
    
    def test_select_fields(self):
        """フィールド選択テスト"""
        builder = QueryBuilder('users')
        builder.select(['id', 'name', 'email'])
        
        assert builder.projection == ['id', 'name', 'email']
    
    def test_build(self):
        """ビルドテスト"""
        builder = QueryBuilder('users')
        query = builder.filter('age', '>', 18).limit(10).build()
        
        assert query['table_name'] == 'users'
        assert query['conditions'] == [{'field': 'age', 'operator': '>', 'value': 18}]
        assert query['limit'] == 10


class TestDynamoDBAdapter:
    """DynamoDBAdapterのテスト"""
    
    @pytest.fixture
    def adapter(self, mock_dynamodb_client):
        """DynamoDBアダプターフィクスチャ"""
        with patch('boto3.client', return_value=mock_dynamodb_client):
            return DynamoDBAdapter(tenant_id='test-tenant', region='ap-northeast-1')
    
    @pytest.mark.asyncio
    async def test_create(self, adapter, mock_user):
        """作成テスト"""
        result = await adapter.create('users', mock_user.__dict__)
        
        assert result is not None
        adapter.client.put_item.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_read(self, adapter):
        """読み取りテスト"""
        result = await adapter.read('users', 'user-001')
        
        assert result is not None
        adapter.client.get_item.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update(self, adapter):
        """更新テスト"""
        updates = {'username': 'newuser', 'updated_at': datetime.utcnow()}
        result = await adapter.update('users', 'user-001', updates)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete(self, adapter):
        """削除テスト"""
        result = await adapter.delete('users', 'user-001')
        
        assert result is True
        adapter.client.delete_item.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_query(self, adapter):
        """クエリテスト"""
        builder = QueryBuilder('users').filter('tenant_id', '=', 'test-tenant')
        results = await adapter.query(builder.build())
        
        assert isinstance(results, list)
        adapter.client.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_batch_write(self, adapter):
        """バッチ書き込みテスト"""
        items = [
            {'id': 'item-1', 'data': 'test1'},
            {'id': 'item-2', 'data': 'test2'}
        ]
        
        with patch.object(adapter.client, 'batch_write_item') as mock_batch:
            mock_batch.return_value = {'UnprocessedItems': {}}
            result = await adapter.batch_write('items', items)
            
            assert result == len(items)
    
    def test_table_name_with_tenant(self, adapter):
        """テナント付きテーブル名テスト"""
        table_name = adapter._get_table_name('users')
        
        assert table_name == 'test-tenant-users'


class TestDatabaseFactory:
    """DatabaseFactoryのテスト"""
    
    def test_create_dynamodb(self):
        """DynamoDBアダプター作成テスト"""
        with patch('makoto_common.database.dynamodb.DynamoDBAdapter') as MockAdapter:
            mock_adapter = Mock()
            MockAdapter.return_value = mock_adapter
            
            adapter = DatabaseFactory.create(
                'dynamodb',
                tenant_id='test-tenant',
                config={'region': 'ap-northeast-1'}
            )
            
            assert adapter == mock_adapter
            MockAdapter.assert_called_once_with(
                tenant_id='test-tenant',
                region='ap-northeast-1'
            )
    
    def test_create_cosmosdb(self):
        """CosmosDBアダプター作成テスト"""
        with patch('makoto_common.database.cosmosdb.CosmosDBAdapter') as MockAdapter:
            mock_adapter = Mock()
            MockAdapter.return_value = mock_adapter
            
            adapter = DatabaseFactory.create(
                'cosmosdb',
                tenant_id='test-tenant',
                config={'endpoint': 'https://test.documents.azure.com'}
            )
            
            assert adapter == mock_adapter
    
    def test_create_invalid_type(self):
        """無効なタイプテスト"""
        with pytest.raises(ValueError) as exc_info:
            DatabaseFactory.create(
                'invalid',
                tenant_id='test-tenant',
                config={}
            )
        
        assert 'Unsupported database type' in str(exc_info.value)
    
    def test_get_supported_types(self):
        """サポートタイプ取得テスト"""
        types = DatabaseFactory.get_supported_types()
        
        assert 'dynamodb' in types
        assert 'cosmosdb' in types