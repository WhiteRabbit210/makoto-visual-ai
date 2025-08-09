"""
pytest設定ファイル
テスト用のフィクスチャと設定
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
import asyncio

# パスを追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../common/python'))

# 環境変数設定
os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-1'
os.environ['ENVIRONMENT'] = 'test'


@pytest.fixture
def event_loop():
    """非同期テスト用のイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_tenant_config():
    """テスト用テナント設定"""
    return {
        'tenant_id': 'test-tenant-001',
        'tenant_name': 'Test Tenant',
        'environment': 'test',
        'region': 'ap-northeast-1',
        'database': {
            'type': 'dynamodb',
            'config': {
                'region': 'ap-northeast-1',
                'endpoint_url': 'http://localhost:8000'
            }
        },
        'storage': {
            'type': 's3',
            'bucket': 'test-tenant-001-storage'
        },
        'llm_config': {
            'provider': 'openai',
            'model': 'gpt-4',
            'api_key': 'test-api-key'
        }
    }


@pytest.fixture
def mock_user():
    """テスト用ユーザー"""
    from makoto_common.types.entities import User
    return User(
        user_id='user-001',
        tenant_id='test-tenant-001',
        username='testuser',
        email='test@example.com',
        role='user',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_chat():
    """テスト用チャット"""
    from makoto_common.types.entities import Chat
    return Chat(
        chat_id='chat-001',
        tenant_id='test-tenant-001',
        user_id='user-001',
        title='Test Chat',
        mode='chat',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def mock_message():
    """テスト用メッセージ"""
    from makoto_common.types.entities import Message
    return Message(
        message_id='msg-001',
        chat_id='chat-001',
        role='user',
        content='Hello, AI!',
        timestamp=datetime.utcnow()
    )


@pytest.fixture
def mock_dynamodb_client():
    """モックDynamoDBクライアント"""
    client = MagicMock()
    
    # テーブル作成
    client.create_table = MagicMock(return_value={'TableDescription': {'TableStatus': 'ACTIVE'}})
    
    # アイテム操作
    client.put_item = MagicMock(return_value={'ResponseMetadata': {'HTTPStatusCode': 200}})
    client.get_item = MagicMock(return_value={
        'Item': {
            'tenant_id': {'S': 'test-tenant-001'},
            'user_id': {'S': 'user-001'},
            'username': {'S': 'testuser'}
        }
    })
    client.query = MagicMock(return_value={
        'Items': [],
        'Count': 0
    })
    client.scan = MagicMock(return_value={
        'Items': [],
        'Count': 0
    })
    client.delete_item = MagicMock(return_value={'ResponseMetadata': {'HTTPStatusCode': 200}})
    
    return client


@pytest.fixture
def mock_s3_client():
    """モックS3クライアント"""
    client = MagicMock()
    
    # バケット操作
    client.create_bucket = MagicMock(return_value={'Location': 'ap-northeast-1'})
    client.list_buckets = MagicMock(return_value={'Buckets': []})
    
    # オブジェクト操作
    client.put_object = MagicMock(return_value={'ETag': '"test-etag"'})
    client.get_object = MagicMock(return_value={
        'Body': MagicMock(read=lambda: b'test content'),
        'ContentType': 'text/plain'
    })
    client.delete_object = MagicMock(return_value={'DeleteMarker': True})
    
    # 署名付きURL
    client.generate_presigned_url = MagicMock(return_value='https://test-url.com')
    
    return client


@pytest.fixture
def mock_openai_client():
    """モックOpenAIクライアント"""
    client = MagicMock()
    
    # チャット完了
    completion = MagicMock()
    completion.choices = [
        MagicMock(
            message=MagicMock(content='AI response'),
            finish_reason='stop'
        )
    ]
    completion.usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=20,
        total_tokens=30
    )
    
    client.chat.completions.create = MagicMock(return_value=completion)
    
    # エンベディング
    embedding = MagicMock()
    embedding.data = [
        MagicMock(embedding=[0.1] * 1536)
    ]
    embedding.usage = MagicMock(total_tokens=10)
    
    client.embeddings.create = MagicMock(return_value=embedding)
    
    return client


@pytest.fixture
def mock_event():
    """テスト用イベント"""
    from makoto_common.events.base import Event
    return Event(
        event_type='test.event',
        tenant_id='test-tenant-001',
        user_id='user-001',
        payload={'test': 'data'}
    )


@pytest.fixture
def mock_lambda_context():
    """Lambda実行コンテキスト"""
    context = MagicMock()
    context.function_name = 'test-function'
    context.function_version = '$LATEST'
    context.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:123456789012:function:test-function'
    context.memory_limit_in_mb = '128'
    context.aws_request_id = 'test-request-id'
    context.log_group_name = '/aws/lambda/test-function'
    context.log_stream_name = '2024/01/01/[$LATEST]test-stream'
    context.get_remaining_time_in_millis = lambda: 300000  # 5分
    
    return context


@pytest.fixture(autouse=True)
def reset_singletons():
    """シングルトンをリセット"""
    # テナントマネージャー
    from makoto_common.tenant.manager import _manager
    if '_manager' in globals():
        globals()['_manager'] = None
    
    # イベントバス
    from makoto_common.events.base import _event_bus
    if '_event_bus' in globals():
        globals()['_event_bus'] = None
    
    yield
    
    # クリーンアップ
    if '_manager' in globals():
        globals()['_manager'] = None
    if '_event_bus' in globals():
        globals()['_event_bus'] = None