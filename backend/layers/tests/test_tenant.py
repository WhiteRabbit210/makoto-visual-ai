"""
テナント管理モジュールのテスト
"""

import pytest
from unittest.mock import Mock, patch
from makoto_common.tenant.manager import TenantManager
from makoto_common.tenant.context import TenantContext
from makoto_common.tenant.isolation import TenantIsolation


class TestTenantManager:
    """TenantManagerのテスト"""
    
    def test_load_config(self, mock_tenant_config):
        """設定読み込みテスト"""
        manager = TenantManager()
        manager.load_config(mock_tenant_config)
        
        assert manager.tenant_id == 'test-tenant-001'
        assert manager.tenant_name == 'Test Tenant'
        assert manager.environment == 'test'
        assert manager.database_config['type'] == 'dynamodb'
    
    def test_get_database_client(self, mock_tenant_config):
        """データベースクライアント取得テスト"""
        manager = TenantManager()
        manager.load_config(mock_tenant_config)
        
        with patch('makoto_common.database.factory.DatabaseFactory.create') as mock_create:
            mock_db = Mock()
            mock_create.return_value = mock_db
            
            db = manager.get_database_client()
            
            assert db == mock_db
            mock_create.assert_called_once_with(
                'dynamodb',
                tenant_id='test-tenant-001',
                config=mock_tenant_config['database']['config']
            )
    
    def test_get_ai_provider(self, mock_tenant_config):
        """AIプロバイダー取得テスト"""
        manager = TenantManager()
        manager.load_config(mock_tenant_config)
        
        with patch('makoto_common.ai.providers.openai.OpenAIProvider') as MockProvider:
            mock_provider = Mock()
            MockProvider.return_value = mock_provider
            
            provider = manager.get_ai_provider()
            
            assert provider == mock_provider
    
    def test_singleton_pattern(self):
        """シングルトンパターンテスト"""
        from makoto_common.tenant.manager import get_tenant_manager
        
        manager1 = get_tenant_manager()
        manager2 = get_tenant_manager()
        
        assert manager1 is manager2


class TestTenantContext:
    """TenantContextのテスト"""
    
    def test_context_initialization(self):
        """コンテキスト初期化テスト"""
        context = TenantContext(
            tenant_id='test-tenant',
            user_id='test-user',
            request_id='req-001'
        )
        
        assert context.tenant_id == 'test-tenant'
        assert context.user_id == 'test-user'
        assert context.request_id == 'req-001'
    
    def test_context_to_dict(self):
        """辞書変換テスト"""
        context = TenantContext(
            tenant_id='test-tenant',
            user_id='test-user'
        )
        
        data = context.to_dict()
        
        assert data['tenant_id'] == 'test-tenant'
        assert data['user_id'] == 'test-user'
        assert 'created_at' in data
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """コンテキストマネージャーテスト"""
        from makoto_common.tenant.context import get_tenant_context, set_tenant_context
        
        context = TenantContext(tenant_id='test-tenant')
        set_tenant_context(context)
        
        retrieved = get_tenant_context()
        assert retrieved.tenant_id == 'test-tenant'


class TestTenantIsolation:
    """TenantIsolationのテスト"""
    
    def test_resource_access_same_tenant(self):
        """同一テナントリソースアクセステスト"""
        isolation = TenantIsolation('tenant-001')
        
        assert isolation.can_access_resource('tenant-001', 'resource-001')
    
    def test_resource_access_different_tenant(self):
        """異なるテナントリソースアクセステスト"""
        isolation = TenantIsolation('tenant-001')
        
        assert not isolation.can_access_resource('tenant-002', 'resource-001')
    
    def test_filter_resources(self):
        """リソースフィルタリングテスト"""
        isolation = TenantIsolation('tenant-001')
        
        resources = [
            {'tenant_id': 'tenant-001', 'id': 'res-1'},
            {'tenant_id': 'tenant-002', 'id': 'res-2'},
            {'tenant_id': 'tenant-001', 'id': 'res-3'},
        ]
        
        filtered = isolation.filter_resources(resources)
        
        assert len(filtered) == 2
        assert all(r['tenant_id'] == 'tenant-001' for r in filtered)
    
    def test_validate_request(self):
        """リクエスト検証テスト"""
        isolation = TenantIsolation('tenant-001')
        
        # 有効なリクエスト
        request = {'tenant_id': 'tenant-001', 'data': 'test'}
        assert isolation.validate_request(request)
        
        # 無効なリクエスト
        request = {'tenant_id': 'tenant-002', 'data': 'test'}
        assert not isolation.validate_request(request)
        
        # テナントIDなし
        request = {'data': 'test'}
        assert not isolation.validate_request(request)