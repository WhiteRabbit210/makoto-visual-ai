"""
ドメインイベント定義
ビジネスロジックに関連するイベント
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from .base import Event, EventType


@dataclass
class DomainEvent(Event):
    """
    ドメインイベント基底クラス
    """
    aggregate_id: Optional[str] = None
    aggregate_type: Optional[str] = None
    version: int = 0
    
    def __post_init__(self):
        """初期化後処理"""
        if not self.event_type and hasattr(self, 'EVENT_TYPE'):
            self.event_type = self.EVENT_TYPE.value if isinstance(self.EVENT_TYPE, Enum) else self.EVENT_TYPE


# ユーザー関連イベント

@dataclass
class UserCreatedEvent(DomainEvent):
    """ユーザー作成イベント"""
    EVENT_TYPE = EventType.USER_CREATED
    
    user_id: str = ""
    username: str = ""
    email: Optional[str] = None
    role: str = "user"
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.user_id
        self.aggregate_type = "User"
        self.payload = {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role
        }


@dataclass
class UserUpdatedEvent(DomainEvent):
    """ユーザー更新イベント"""
    EVENT_TYPE = EventType.USER_UPDATED
    
    user_id: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.user_id
        self.aggregate_type = "User"
        self.payload = {
            'user_id': self.user_id,
            'changes': self.changes
        }


@dataclass
class UserDeletedEvent(DomainEvent):
    """ユーザー削除イベント"""
    EVENT_TYPE = EventType.USER_DELETED
    
    user_id: str = ""
    reason: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.user_id
        self.aggregate_type = "User"
        self.payload = {
            'user_id': self.user_id,
            'reason': self.reason
        }


# チャット関連イベント

@dataclass
class ChatCreatedEvent(DomainEvent):
    """チャット作成イベント"""
    EVENT_TYPE = EventType.CHAT_CREATED
    
    chat_id: str = ""
    user_id: str = ""
    title: Optional[str] = None
    mode: str = "chat"
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.chat_id
        self.aggregate_type = "Chat"
        self.payload = {
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'title': self.title,
            'mode': self.mode
        }


@dataclass
class MessageSentEvent(DomainEvent):
    """メッセージ送信イベント"""
    EVENT_TYPE = EventType.MESSAGE_SENT
    
    message_id: str = ""
    chat_id: str = ""
    user_id: str = ""
    content: str = ""
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.chat_id
        self.aggregate_type = "Chat"
        self.payload = {
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'user_id': self.user_id,
            'content': self.content,
            'attachments': self.attachments
        }


@dataclass
class MessageReceivedEvent(DomainEvent):
    """メッセージ受信イベント（AI応答）"""
    EVENT_TYPE = EventType.MESSAGE_RECEIVED
    
    message_id: str = ""
    chat_id: str = ""
    agent_id: str = ""
    content: str = ""
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.chat_id
        self.aggregate_type = "Chat"
        self.payload = {
            'message_id': self.message_id,
            'chat_id': self.chat_id,
            'agent_id': self.agent_id,
            'content': self.content,
            'model': self.model,
            'tokens_used': self.tokens_used
        }


# タスク関連イベント

@dataclass
class TaskCreatedEvent(DomainEvent):
    """タスク作成イベント"""
    EVENT_TYPE = EventType.TASK_CREATED
    
    task_id: str = ""
    user_id: str = ""
    title: str = ""
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.task_id
        self.aggregate_type = "Task"
        self.payload = {
            'task_id': self.task_id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None
        }


@dataclass
class TaskCompletedEvent(DomainEvent):
    """タスク完了イベント"""
    EVENT_TYPE = EventType.TASK_COMPLETED
    
    task_id: str = ""
    completed_by: str = ""
    completion_time: datetime = field(default_factory=datetime.utcnow)
    result: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.task_id
        self.aggregate_type = "Task"
        self.payload = {
            'task_id': self.task_id,
            'completed_by': self.completed_by,
            'completion_time': self.completion_time.isoformat(),
            'result': self.result
        }


@dataclass
class TaskFailedEvent(DomainEvent):
    """タスク失敗イベント"""
    EVENT_TYPE = EventType.TASK_FAILED
    
    task_id: str = ""
    error_message: str = ""
    error_code: Optional[str] = None
    retry_count: int = 0
    can_retry: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.task_id
        self.aggregate_type = "Task"
        self.payload = {
            'task_id': self.task_id,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'retry_count': self.retry_count,
            'can_retry': self.can_retry
        }


# エージェント関連イベント

@dataclass
class AgentStartedEvent(DomainEvent):
    """エージェント開始イベント"""
    EVENT_TYPE = EventType.AGENT_STARTED
    
    agent_id: str = ""
    agent_type: str = ""
    task_id: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.agent_id
        self.aggregate_type = "Agent"
        self.payload = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'task_id': self.task_id,
            'parameters': self.parameters
        }


@dataclass
class AgentCompletedEvent(DomainEvent):
    """エージェント完了イベント"""
    EVENT_TYPE = EventType.AGENT_COMPLETED
    
    agent_id: str = ""
    agent_type: str = ""
    task_id: Optional[str] = None
    result: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.agent_id
        self.aggregate_type = "Agent"
        self.payload = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'task_id': self.task_id,
            'result': self.result,
            'execution_time': self.execution_time
        }


@dataclass
class AgentFailedEvent(DomainEvent):
    """エージェント失敗イベント"""
    EVENT_TYPE = EventType.AGENT_FAILED
    
    agent_id: str = ""
    agent_type: str = ""
    task_id: Optional[str] = None
    error_message: str = ""
    error_code: Optional[str] = None
    can_retry: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.agent_id
        self.aggregate_type = "Agent"
        self.payload = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'task_id': self.task_id,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'can_retry': self.can_retry
        }


@dataclass
class AgentProgressEvent(DomainEvent):
    """エージェント進捗イベント"""
    EVENT_TYPE = EventType.AGENT_PROGRESS
    
    agent_id: str = ""
    agent_type: str = ""
    task_id: Optional[str] = None
    progress: float = 0.0  # 0.0 - 1.0
    message: Optional[str] = None
    current_step: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.agent_id
        self.aggregate_type = "Agent"
        self.payload = {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'task_id': self.task_id,
            'progress': self.progress,
            'message': self.message,
            'current_step': self.current_step
        }


# ライブラリ関連イベント

@dataclass
class LibraryItemCreatedEvent(DomainEvent):
    """ライブラリアイテム作成イベント"""
    EVENT_TYPE = EventType.LIBRARY_ITEM_CREATED
    
    item_id: str = ""
    library_id: str = ""
    item_type: str = ""
    title: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.item_id
        self.aggregate_type = "LibraryItem"
        self.payload = {
            'item_id': self.item_id,
            'library_id': self.library_id,
            'item_type': self.item_type,
            'title': self.title,
            'content': self.content,
            'tags': self.tags
        }


@dataclass
class LibraryItemUpdatedEvent(DomainEvent):
    """ライブラリアイテム更新イベント"""
    EVENT_TYPE = EventType.LIBRARY_ITEM_UPDATED
    
    item_id: str = ""
    library_id: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)
    updated_by: str = ""
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.item_id
        self.aggregate_type = "LibraryItem"
        self.payload = {
            'item_id': self.item_id,
            'library_id': self.library_id,
            'changes': self.changes,
            'updated_by': self.updated_by
        }


@dataclass
class LibraryItemDeletedEvent(DomainEvent):
    """ライブラリアイテム削除イベント"""
    EVENT_TYPE = EventType.LIBRARY_ITEM_DELETED
    
    item_id: str = ""
    library_id: str = ""
    deleted_by: str = ""
    reason: Optional[str] = None
    
    def __post_init__(self):
        super().__post_init__()
        self.aggregate_id = self.item_id
        self.aggregate_type = "LibraryItem"
        self.payload = {
            'item_id': self.item_id,
            'library_id': self.library_id,
            'deleted_by': self.deleted_by,
            'reason': self.reason
        }


# イベントファクトリー

class EventFactory:
    """
    イベントファクトリー
    イベントタイプから適切なイベントクラスを生成
    """
    
    _event_classes = {
        EventType.USER_CREATED: UserCreatedEvent,
        EventType.USER_UPDATED: UserUpdatedEvent,
        EventType.USER_DELETED: UserDeletedEvent,
        EventType.CHAT_CREATED: ChatCreatedEvent,
        EventType.MESSAGE_SENT: MessageSentEvent,
        EventType.MESSAGE_RECEIVED: MessageReceivedEvent,
        EventType.TASK_CREATED: TaskCreatedEvent,
        EventType.TASK_COMPLETED: TaskCompletedEvent,
        EventType.TASK_FAILED: TaskFailedEvent,
        EventType.AGENT_STARTED: AgentStartedEvent,
        EventType.AGENT_COMPLETED: AgentCompletedEvent,
        EventType.AGENT_FAILED: AgentFailedEvent,
        EventType.AGENT_PROGRESS: AgentProgressEvent,
        EventType.LIBRARY_ITEM_CREATED: LibraryItemCreatedEvent,
        EventType.LIBRARY_ITEM_UPDATED: LibraryItemUpdatedEvent,
        EventType.LIBRARY_ITEM_DELETED: LibraryItemDeletedEvent,
    }
    
    @classmethod
    def create(
        cls,
        event_type: EventType,
        **kwargs
    ) -> DomainEvent:
        """
        イベントを作成
        
        Args:
            event_type: イベントタイプ
            **kwargs: イベントパラメータ
            
        Returns:
            ドメインイベント
        """
        event_class = cls._event_classes.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return event_class(**kwargs)
    
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any]
    ) -> DomainEvent:
        """
        辞書からイベントを作成
        
        Args:
            data: イベントデータ
            
        Returns:
            ドメインイベント
        """
        event_type_str = data.get('event_type')
        if not event_type_str:
            raise ValueError("event_type is required")
        
        # EventTypeに変換
        event_type = None
        for et in EventType:
            if et.value == event_type_str:
                event_type = et
                break
        
        if not event_type:
            raise ValueError(f"Unknown event type: {event_type_str}")
        
        event_class = cls._event_classes.get(event_type)
        if not event_class:
            raise ValueError(f"No event class for type: {event_type}")
        
        return event_class.from_dict(data)