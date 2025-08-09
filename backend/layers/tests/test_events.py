"""
イベント処理モジュールのテスト
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from makoto_common.events.base import (
    Event, EventType, EventHandler, AsyncEventHandler,
    LocalEventBus, SQSEventBus, EventBridgeEventBus
)
from makoto_common.events.domain_events import (
    UserCreatedEvent, ChatCreatedEvent, MessageSentEvent,
    TaskCreatedEvent, AgentStartedEvent, EventFactory
)


class TestEvent:
    """Eventクラスのテスト"""
    
    def test_event_creation(self):
        """イベント作成テスト"""
        event = Event(
            event_type='test.event',
            tenant_id='tenant-001',
            user_id='user-001',
            payload={'data': 'test'}
        )
        
        assert event.event_type == 'test.event'
        assert event.tenant_id == 'tenant-001'
        assert event.user_id == 'user-001'
        assert event.payload == {'data': 'test'}
        assert event.event_id is not None
        assert event.timestamp is not None
    
    def test_event_to_dict(self):
        """辞書変換テスト"""
        event = Event(event_type='test.event')
        data = event.to_dict()
        
        assert 'event_id' in data
        assert 'event_type' in data
        assert 'timestamp' in data
        assert data['event_type'] == 'test.event'
    
    def test_event_to_json(self):
        """JSON変換テスト"""
        event = Event(event_type='test.event')
        json_str = event.to_json()
        
        assert isinstance(json_str, str)
        assert 'test.event' in json_str
    
    def test_event_from_dict(self):
        """辞書からの作成テスト"""
        data = {
            'event_type': 'test.event',
            'tenant_id': 'tenant-001',
            'payload': {'data': 'test'}
        }
        
        event = Event.from_dict(data)
        
        assert event.event_type == 'test.event'
        assert event.tenant_id == 'tenant-001'
        assert event.payload == {'data': 'test'}


class TestEventHandler:
    """EventHandlerのテスト"""
    
    @pytest.mark.asyncio
    async def test_async_handler(self):
        """非同期ハンドラーテスト"""
        mock_func = AsyncMock(return_value='result')
        handler = AsyncEventHandler(mock_func)
        
        event = Event(event_type='test.event')
        result = await handler.handle(event)
        
        assert result == 'result'
        mock_func.assert_called_once_with(event)
    
    @pytest.mark.asyncio
    async def test_sync_handler(self):
        """同期ハンドラーテスト"""
        mock_func = Mock(return_value='result')
        handler = AsyncEventHandler(mock_func)
        
        event = Event(event_type='test.event')
        result = await handler.handle(event)
        
        mock_func.assert_called_once_with(event)


class TestLocalEventBus:
    """LocalEventBusのテスト"""
    
    @pytest.mark.asyncio
    async def test_publish_subscribe(self):
        """パブリッシュ・サブスクライブテスト"""
        bus = LocalEventBus()
        received_events = []
        
        async def handler(event):
            received_events.append(event)
        
        await bus.subscribe('test.event', AsyncEventHandler(handler))
        
        event = Event(event_type='test.event', payload={'test': 'data'})
        await bus.publish(event)
        
        # イベント処理を待つ
        await asyncio.sleep(0.1)
        
        assert len(received_events) == 1
        assert received_events[0].payload == {'test': 'data'}
    
    @pytest.mark.asyncio
    async def test_multiple_handlers(self):
        """複数ハンドラーテスト"""
        bus = LocalEventBus()
        results = []
        
        async def handler1(event):
            results.append('handler1')
        
        async def handler2(event):
            results.append('handler2')
        
        await bus.subscribe('test.event', AsyncEventHandler(handler1))
        await bus.subscribe('test.event', AsyncEventHandler(handler2))
        
        event = Event(event_type='test.event')
        await bus.publish(event)
        
        await asyncio.sleep(0.1)
        
        assert 'handler1' in results
        assert 'handler2' in results
    
    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """購読解除テスト"""
        bus = LocalEventBus()
        received = []
        
        async def handler(event):
            received.append(event)
        
        handler_obj = AsyncEventHandler(handler)
        await bus.subscribe('test.event', handler_obj)
        await bus.unsubscribe('test.event', handler_obj)
        
        event = Event(event_type='test.event')
        await bus.publish(event)
        
        await asyncio.sleep(0.1)
        
        assert len(received) == 0


class TestDomainEvents:
    """ドメインイベントのテスト"""
    
    def test_user_created_event(self):
        """ユーザー作成イベントテスト"""
        event = UserCreatedEvent(
            user_id='user-001',
            username='testuser',
            email='test@example.com',
            role='admin'
        )
        
        assert event.event_type == EventType.USER_CREATED.value
        assert event.aggregate_id == 'user-001'
        assert event.aggregate_type == 'User'
        assert event.payload['username'] == 'testuser'
    
    def test_chat_created_event(self):
        """チャット作成イベントテスト"""
        event = ChatCreatedEvent(
            chat_id='chat-001',
            user_id='user-001',
            title='Test Chat',
            mode='agent'
        )
        
        assert event.event_type == EventType.CHAT_CREATED.value
        assert event.aggregate_id == 'chat-001'
        assert event.payload['mode'] == 'agent'
    
    def test_message_sent_event(self):
        """メッセージ送信イベントテスト"""
        event = MessageSentEvent(
            message_id='msg-001',
            chat_id='chat-001',
            user_id='user-001',
            content='Hello!'
        )
        
        assert event.event_type == EventType.MESSAGE_SENT.value
        assert event.aggregate_id == 'chat-001'
        assert event.payload['content'] == 'Hello!'
    
    def test_task_created_event(self):
        """タスク作成イベントテスト"""
        event = TaskCreatedEvent(
            task_id='task-001',
            user_id='user-001',
            title='Test Task',
            priority='high'
        )
        
        assert event.event_type == EventType.TASK_CREATED.value
        assert event.aggregate_id == 'task-001'
        assert event.payload['priority'] == 'high'


class TestEventFactory:
    """EventFactoryのテスト"""
    
    def test_create_event(self):
        """イベント作成テスト"""
        event = EventFactory.create(
            EventType.USER_CREATED,
            user_id='user-001',
            username='testuser'
        )
        
        assert isinstance(event, UserCreatedEvent)
        assert event.user_id == 'user-001'
        assert event.username == 'testuser'
    
    def test_from_dict(self):
        """辞書からの作成テスト"""
        data = {
            'event_type': 'user.created',
            'user_id': 'user-001',
            'username': 'testuser',
            'email': 'test@example.com',
            'role': 'user'
        }
        
        event = EventFactory.from_dict(data)
        
        assert isinstance(event, UserCreatedEvent)
        assert event.user_id == 'user-001'
    
    def test_invalid_event_type(self):
        """無効なイベントタイプテスト"""
        with pytest.raises(ValueError):
            EventFactory.create('invalid.type', data='test')