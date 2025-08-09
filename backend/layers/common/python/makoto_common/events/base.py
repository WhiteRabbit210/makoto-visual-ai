"""
イベント処理基底クラス
イベント駆動アーキテクチャの基盤
"""

import json
import uuid
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Type, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(Enum):
    """イベントタイプ"""
    # ユーザー関連
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    
    # チャット関連
    CHAT_CREATED = "chat.created"
    CHAT_UPDATED = "chat.updated"
    MESSAGE_SENT = "message.sent"
    MESSAGE_RECEIVED = "message.received"
    
    # タスク関連
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    # エージェント関連
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_PROGRESS = "agent.progress"
    
    # ライブラリ関連
    LIBRARY_ITEM_CREATED = "library.item.created"
    LIBRARY_ITEM_UPDATED = "library.item.updated"
    LIBRARY_ITEM_DELETED = "library.item.deleted"
    
    # システム関連
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"


@dataclass
class Event:
    """
    基底イベントクラス
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'tenant_id': self.tenant_id,
            'user_id': self.user_id,
            'correlation_id': self.correlation_id,
            'metadata': self.metadata,
            'payload': self.payload
        }
    
    def to_json(self) -> str:
        """JSON文字列に変換"""
        return json.dumps(self.to_dict(), default=str)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """辞書から作成"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """JSON文字列から作成"""
        return cls.from_dict(json.loads(json_str))


class EventHandler(ABC):
    """
    イベントハンドラー基底クラス
    """
    
    @abstractmethod
    async def handle(self, event: Event) -> Any:
        """
        イベントを処理
        
        Args:
            event: イベント
            
        Returns:
            処理結果
        """
        pass
    
    def can_handle(self, event: Event) -> bool:
        """
        このハンドラーがイベントを処理できるか判定
        
        Args:
            event: イベント
            
        Returns:
            処理可能な場合True
        """
        return True


class AsyncEventHandler(EventHandler):
    """
    非同期イベントハンドラー
    """
    
    def __init__(self, handler_func: Callable[[Event], Any]):
        """
        初期化
        
        Args:
            handler_func: ハンドラー関数
        """
        self.handler_func = handler_func
    
    async def handle(self, event: Event) -> Any:
        """非同期でイベントを処理"""
        if asyncio.iscoroutinefunction(self.handler_func):
            return await self.handler_func(event)
        else:
            return await asyncio.get_event_loop().run_in_executor(
                None, self.handler_func, event
            )


class SyncEventHandler(EventHandler):
    """
    同期イベントハンドラー
    """
    
    def __init__(self, handler_func: Callable[[Event], Any]):
        """
        初期化
        
        Args:
            handler_func: ハンドラー関数
        """
        self.handler_func = handler_func
    
    async def handle(self, event: Event) -> Any:
        """同期的にイベントを処理"""
        return self.handler_func(event)


class BatchEventHandler(EventHandler):
    """
    バッチイベントハンドラー
    複数のイベントをまとめて処理
    """
    
    def __init__(
        self,
        handler_func: Callable[[List[Event]], Any],
        batch_size: int = 10,
        timeout: float = 1.0
    ):
        """
        初期化
        
        Args:
            handler_func: ハンドラー関数
            batch_size: バッチサイズ
            timeout: タイムアウト秒数
        """
        self.handler_func = handler_func
        self.batch_size = batch_size
        self.timeout = timeout
        self.buffer: List[Event] = []
        self.last_flush = datetime.utcnow()
    
    async def handle(self, event: Event) -> Any:
        """イベントをバッファに追加"""
        self.buffer.append(event)
        
        # バッチサイズまたはタイムアウトに達したら処理
        if len(self.buffer) >= self.batch_size or \
           (datetime.utcnow() - self.last_flush).total_seconds() > self.timeout:
            return await self.flush()
    
    async def flush(self) -> Any:
        """バッファ内のイベントを処理"""
        if not self.buffer:
            return None
        
        events = self.buffer.copy()
        self.buffer.clear()
        self.last_flush = datetime.utcnow()
        
        if asyncio.iscoroutinefunction(self.handler_func):
            return await self.handler_func(events)
        else:
            return self.handler_func(events)


class EventBus(ABC):
    """
    イベントバス基底クラス
    """
    
    @abstractmethod
    async def publish(self, event: Event):
        """
        イベントを発行
        
        Args:
            event: イベント
        """
        pass
    
    @abstractmethod
    async def subscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """
        イベントを購読
        
        Args:
            event_type: イベントタイプ
            handler: イベントハンドラー
        """
        pass
    
    @abstractmethod
    async def unsubscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """
        購読を解除
        
        Args:
            event_type: イベントタイプ
            handler: イベントハンドラー
        """
        pass


class LocalEventBus(EventBus):
    """
    ローカルイベントバス
    プロセス内でのイベント処理
    """
    
    def __init__(self):
        """初期化"""
        self.handlers: Dict[str, List[EventHandler]] = {}
        self.middleware: List[Callable] = []
    
    async def publish(self, event: Event):
        """イベントを発行"""
        event_type = event.event_type
        
        # ミドルウェア実行
        for mw in self.middleware:
            event = await mw(event) if asyncio.iscoroutinefunction(mw) else mw(event)
            if event is None:
                return
        
        # ハンドラー実行
        if event_type in self.handlers:
            tasks = []
            for handler in self.handlers[event_type]:
                if handler.can_handle(event):
                    tasks.append(handler.handle(event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug(f"イベント発行: {event_type}")
    
    async def subscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """イベントを購読"""
        if isinstance(event_type, EventType):
            event_type = event_type.value
        
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
        logger.debug(f"イベント購読: {event_type}")
    
    async def unsubscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """購読を解除"""
        if isinstance(event_type, EventType):
            event_type = event_type.value
        
        if event_type in self.handlers:
            self.handlers[event_type].remove(handler)
            logger.debug(f"購読解除: {event_type}")
    
    def add_middleware(self, middleware: Callable):
        """ミドルウェアを追加"""
        self.middleware.append(middleware)


class SQSEventBus(EventBus):
    """
    AWS SQSイベントバス
    """
    
    def __init__(self, queue_url: str, region: Optional[str] = None):
        """
        初期化
        
        Args:
            queue_url: SQSキューURL
            region: AWSリージョン
        """
        from ..aws_clients import get_aws_client_manager
        
        self.queue_url = queue_url
        self.manager = get_aws_client_manager(region=region)
        self.sqs = self.manager.sqs
    
    async def publish(self, event: Event):
        """SQSにイベントを発行"""
        response = self.sqs.send_message(
            QueueUrl=self.queue_url,
            MessageBody=event.to_json(),
            MessageAttributes={
                'event_type': {
                    'StringValue': event.event_type,
                    'DataType': 'String'
                },
                'tenant_id': {
                    'StringValue': event.tenant_id or '',
                    'DataType': 'String'
                }
            }
        )
        
        logger.debug(f"SQSイベント発行: {event.event_type}, MessageId: {response['MessageId']}")
    
    async def subscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """SQSイベントの購読（ポーリング）"""
        # 実装はLambda関数やワーカープロセスで行う
        raise NotImplementedError("SQS購読はLambda関数で実装してください")
    
    async def unsubscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """購読解除"""
        # SQSでは明示的な購読解除は不要
        pass


class EventBridgeEventBus(EventBus):
    """
    AWS EventBridgeイベントバス
    """
    
    def __init__(
        self,
        bus_name: str = 'default',
        region: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            bus_name: イベントバス名
            region: AWSリージョン
        """
        from ..aws_clients import get_aws_client_manager
        
        self.bus_name = bus_name
        self.manager = get_aws_client_manager(region=region)
        self.eventbridge = self.manager.eventbridge
    
    async def publish(self, event: Event):
        """EventBridgeにイベントを発行"""
        entry = {
            'Source': 'makoto.visual.ai',
            'DetailType': event.event_type,
            'Detail': event.to_json(),
            'EventBusName': self.bus_name
        }
        
        if event.correlation_id:
            entry['TraceHeader'] = event.correlation_id
        
        response = self.eventbridge.put_events(Entries=[entry])
        
        if response['FailedEntryCount'] > 0:
            logger.error(f"EventBridge発行失敗: {response['Entries']}")
        else:
            logger.debug(f"EventBridgeイベント発行: {event.event_type}")
    
    async def subscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """EventBridgeイベントの購読（ルール作成）"""
        # 実装はCloudFormationやTerraformで行う
        raise NotImplementedError("EventBridge購読はインフラ定義で実装してください")
    
    async def unsubscribe(
        self,
        event_type: Union[str, EventType],
        handler: EventHandler
    ):
        """購読解除"""
        # EventBridgeでは明示的な購読解除は不要
        pass


class EventStore(ABC):
    """
    イベントストア基底クラス
    イベントソーシングのための永続化
    """
    
    @abstractmethod
    async def append(self, event: Event):
        """
        イベントを追加
        
        Args:
            event: イベント
        """
        pass
    
    @abstractmethod
    async def get_events(
        self,
        aggregate_id: str,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None
    ) -> List[Event]:
        """
        イベントを取得
        
        Args:
            aggregate_id: 集約ID
            from_version: 開始バージョン
            to_version: 終了バージョン
            
        Returns:
            イベントリスト
        """
        pass
    
    @abstractmethod
    async def get_snapshot(
        self,
        aggregate_id: str,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        スナップショットを取得
        
        Args:
            aggregate_id: 集約ID
            version: バージョン
            
        Returns:
            スナップショット
        """
        pass
    
    @abstractmethod
    async def save_snapshot(
        self,
        aggregate_id: str,
        version: int,
        snapshot: Dict[str, Any]
    ):
        """
        スナップショットを保存
        
        Args:
            aggregate_id: 集約ID
            version: バージョン
            snapshot: スナップショットデータ
        """
        pass


# グローバルイベントバス
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """グローバルイベントバスを取得"""
    global _event_bus
    if _event_bus is None:
        _event_bus = LocalEventBus()
    return _event_bus


def set_event_bus(bus: EventBus):
    """グローバルイベントバスを設定"""
    global _event_bus
    _event_bus = bus


# 便利関数

async def publish_event(event: Event):
    """イベントを発行"""
    bus = get_event_bus()
    await bus.publish(event)


async def subscribe_event(
    event_type: Union[str, EventType],
    handler: Union[EventHandler, Callable]
):
    """イベントを購読"""
    bus = get_event_bus()
    
    if not isinstance(handler, EventHandler):
        handler = AsyncEventHandler(handler)
    
    await bus.subscribe(event_type, handler)


def event_handler(event_type: Union[str, EventType]):
    """
    イベントハンドラーデコレーター
    
    Example:
        ```python
        @event_handler(EventType.USER_CREATED)
        async def handle_user_created(event: Event):
            print(f"User created: {event.payload}")
        ```
    """
    def decorator(func: Callable):
        # 起動時に自動購読
        asyncio.create_task(
            subscribe_event(event_type, func)
        )
        return func
    
    return decorator