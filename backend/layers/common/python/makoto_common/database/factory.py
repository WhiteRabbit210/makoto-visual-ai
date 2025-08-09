"""
データベースファクトリ
テナント設定に基づいて適切なデータベースアダプタを生成
"""

import os
from typing import Optional
import logging

from .interface import DatabaseInterface
from .dynamodb import DynamoDBAdapter
from .cosmosdb import CosmosDBAdapter
from ..types.primitives import TenantId
from ..tenant.context import get_current_tenant
from ..tenant.manager import CloudProvider, TenantManager

logger = logging.getLogger(__name__)


class DatabaseFactory:
    """
    データベースファクトリ
    テナントのクラウドプロバイダーに応じてアダプタを選択
    """
    
    _instances = {}  # シングルトンキャッシュ
    
    @classmethod
    def get_adapter(
        cls,
        tenant_id: Optional[TenantId] = None,
        cloud_provider: Optional[CloudProvider] = None
    ) -> DatabaseInterface:
        """
        データベースアダプタを取得
        
        Args:
            tenant_id: テナントID
            cloud_provider: クラウドプロバイダー（指定しない場合はテナント設定から取得）
            
        Returns:
            データベースアダプタ
        """
        # テナントIDの取得
        if not tenant_id:
            context = get_current_tenant()
            if context:
                tenant_id = context.tenant_id
            else:
                # コンテキストがない場合はデフォルト
                tenant_id = TenantId("default")
        
        # キャッシュチェック
        cache_key = str(tenant_id)
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # クラウドプロバイダーの決定
        if not cloud_provider:
            # テナントマネージャーから取得
            tenant_manager = TenantManager()
            tenant_info = tenant_manager.get_tenant(tenant_id)
            
            if tenant_info and tenant_info.config:
                cloud_provider = tenant_info.config.cloud_provider
            else:
                # デフォルトはAWS
                cloud_provider = CloudProvider.AWS
        
        # アダプタの生成
        adapter = cls._create_adapter(tenant_id, cloud_provider)
        
        # キャッシュに保存
        cls._instances[cache_key] = adapter
        
        logger.info(
            f"データベースアダプタ作成: {cloud_provider.value}",
            extra={'tenant_id': tenant_id}
        )
        
        return adapter
    
    @staticmethod
    def _create_adapter(
        tenant_id: TenantId,
        cloud_provider: CloudProvider
    ) -> DatabaseInterface:
        """
        アダプタを作成
        
        Args:
            tenant_id: テナントID
            cloud_provider: クラウドプロバイダー
            
        Returns:
            データベースアダプタ
            
        Raises:
            ValueError: サポートされていないプロバイダーの場合
        """
        if cloud_provider == CloudProvider.AWS:
            # AWS DynamoDB
            return DynamoDBAdapter(
                tenant_id=tenant_id,
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-1'),
                endpoint_url=os.environ.get('DYNAMODB_ENDPOINT')  # ローカルテスト用
            )
            
        elif cloud_provider == CloudProvider.AZURE:
            # Azure CosmosDB
            return CosmosDBAdapter(
                tenant_id=tenant_id,
                endpoint=os.environ.get('COSMOS_ENDPOINT'),
                key=os.environ.get('COSMOS_KEY'),
                database_name=os.environ.get('COSMOS_DATABASE', 'makoto')
            )
            
        elif cloud_provider == CloudProvider.CUSTOM:
            # カスタム実装
            # デフォルトでDynamoDB使用
            logger.warning(
                "カスタムプロバイダーは未実装。DynamoDBを使用します。",
                extra={'tenant_id': tenant_id}
            )
            return DynamoDBAdapter(
                tenant_id=tenant_id,
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-1')
            )
            
        else:
            raise ValueError(f"サポートされていないクラウドプロバイダー: {cloud_provider}")
    
    @classmethod
    def clear_cache(cls, tenant_id: Optional[TenantId] = None):
        """
        キャッシュをクリア
        
        Args:
            tenant_id: 特定テナントのキャッシュをクリア（Noneの場合は全体）
        """
        if tenant_id:
            cache_key = str(tenant_id)
            if cache_key in cls._instances:
                del cls._instances[cache_key]
                logger.info(
                    f"データベースアダプタキャッシュクリア: {tenant_id}"
                )
        else:
            cls._instances.clear()
            logger.info("全データベースアダプタキャッシュクリア")


def get_database() -> DatabaseInterface:
    """
    現在のコンテキストに基づいてデータベースアダプタを取得
    
    Returns:
        データベースアダプタ
    """
    return DatabaseFactory.get_adapter()