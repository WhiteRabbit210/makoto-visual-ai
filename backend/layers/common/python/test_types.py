#!/usr/bin/env python3
"""
型定義のテスト

makoto/backend/layers/common/python/makoto_common/types の型定義が
正しく動作することを確認するテスト
"""

import sys
import json
from datetime import datetime
from typing import List

# テスト対象のインポート
from makoto_common.types.primitives import (
    TenantId, UserId, ChatId, MessageId, FileId, LibraryId
)
from makoto_common.types.entities import (
    ChatMode, ChatSettings, Message, Chat, User, Library, File as FileEntity
)
from makoto_common.types.api import (
    BaseRequest, BaseResponse, ErrorCode, ErrorDetail,
    PaginationRequest, PaginatedResponse, PaginationMeta,
    StreamingResponse, TextChunkEvent, ImageGeneratingEvent,
    ImageGeneratedEvent, GeneratedImage, StreamErrorEvent, StreamCompleteEvent
)


def test_primitives():
    """プリミティブ型のテスト"""
    print("1. プリミティブ型のテスト...")
    
    # 型の作成
    tenant_id = TenantId("tenant-123")
    user_id = UserId("user-456")
    chat_id = ChatId("chat-789")
    
    assert isinstance(tenant_id, str)
    assert tenant_id == "tenant-123"
    print("  ✅ プリミティブ型: OK")


def test_entities():
    """エンティティ型のテスト"""
    print("2. エンティティ型のテスト...")
    
    # ChatSettingsの作成
    settings = ChatSettings(
        system_prompt="You are a helpful assistant",
        temperature=0.7,
        active_modes=["chat", "rag"]  # Literal型は値そのものを使用
    )
    assert settings.temperature == 0.7
    assert len(settings.active_modes) == 2
    
    # Userの作成
    user = User(
        id="user-001",
        tenant_id="tenant-001",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="admin",
        updated_by="admin",
        username="testuser",
        email="test@example.com"
    )
    assert user.username == "testuser"
    assert user.status == "active"  # デフォルト値
    
    # Chatの作成
    chat = Chat(
        id="chat-001",
        tenant_id="tenant-001",
        user_id="user-001",
        title="Test Chat",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="user-001",
        updated_by="user-001"
    )
    assert chat.title == "Test Chat"
    assert chat.model == "gpt-4"  # デフォルト値
    
    # Messageの作成
    message = Message(
        id="msg-001",
        tenant_id="tenant-001",
        chat_id="chat-001",
        role="user",
        text="こんにちは",  # textフィールド（ドキュメント準拠）
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="user-001",
        updated_by="user-001"
    )
    assert message.text == "こんにちは"
    assert message.role == "user"
    
    print("  ✅ エンティティ型: OK")


def test_api_types():
    """API型のテスト"""
    print("3. API型のテスト...")
    
    # BaseRequestの作成
    request = BaseRequest(
        tenant_id="tenant-001",
        user_id="user-001"
    )
    assert request.tenant_id == "tenant-001"
    assert hasattr(request, 'request_id')
    
    # BaseResponseの作成
    response = BaseResponse.ok(
        data={"message": "Success"},
        request_id="req-001"
    )
    assert response.success == True
    assert response.data["message"] == "Success"
    
    # エラーレスポンスの作成
    error_response = BaseResponse.error(
        error_code=ErrorCode.NOT_FOUND,
        message="リソースが見つかりません",
        request_id="req-002"
    )
    assert error_response.success == False
    assert error_response.error.code == ErrorCode.NOT_FOUND
    
    # PaginationMetaの作成
    meta = PaginationMeta.create(total=100, page=2, limit=20)
    assert meta.total == 100
    assert meta.pages == 5
    assert meta.has_next == True
    assert meta.has_prev == True
    
    print("  ✅ API型: OK")


def test_sse_types():
    """SSE型のテスト"""
    print("4. SSE型のテスト...")
    
    # TextChunkEventの作成
    text_event = TextChunkEvent(
        type="text",
        content="Hello, world!"
    )
    assert text_event.type == "text"
    assert text_event.content == "Hello, world!"
    
    # GeneratedImageの作成
    image = GeneratedImage(
        url="https://example.com/image.png",
        prompt="A beautiful sunset",
        size="1024x1024",
        style="vivid"
    )
    assert image.url == "https://example.com/image.png"
    assert image.size == "1024x1024"
    
    # ImageGeneratedEventの作成
    image_event = ImageGeneratedEvent(
        type="images",
        images=[image]
    )
    assert image_event.type == "images"
    assert len(image_event.images) == 1
    assert image_event.images[0].prompt == "A beautiful sunset"
    
    # StreamCompleteEventの作成
    complete_event = StreamCompleteEvent(
        type="done",
        done=True,
        chat_id="chat-001",
        message_id="msg-001"
    )
    assert complete_event.done == True
    assert complete_event.chat_id == "chat-001"
    
    # StreamingResponseの作成とSSE変換
    streaming = StreamingResponse(
        success=True,
        data={"content": "テスト"},
        event_type="message",
        event_id="evt-001"
    )
    sse_output = streaming.to_sse()
    assert "id: evt-001" in sse_output
    assert "event: message" in sse_output
    assert "data:" in sse_output
    
    print("  ✅ SSE型: OK")


def test_field_compatibility():
    """フィールド互換性のテスト"""
    print("5. フィールド互換性のテスト...")
    
    # Messageのtextフィールド確認（contentではない）
    message = Message(
        id="msg-002",
        tenant_id="tenant-001",
        chat_id="chat-001",
        role="assistant",
        text="AIからの返答です",  # textフィールドが必須
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="system",
        updated_by="system"
    )
    
    # textフィールドが存在することを確認
    assert hasattr(message, 'text')
    assert message.text == "AIからの返答です"
    
    # contentフィールドが存在しないことを確認
    assert not hasattr(message, 'content')
    
    print("  ✅ フィールド互換性: OK")


def test_dataclass_inheritance():
    """dataclass継承のテスト"""
    print("6. dataclass継承のテスト...")
    
    # デフォルト値の問題が解決されているか確認
    try:
        # すべての必須フィールドを指定してインスタンス作成
        library = Library(
            id="lib-001",
            tenant_id="tenant-001",
            name="Test Library",
            type="document",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by="user-001",
            updated_by="user-001"
        )
        assert library.name == "Test Library"
        assert library.index_status == "pending"  # デフォルト値
        print("  ✅ dataclass継承: OK")
    except TypeError as e:
        print(f"  ❌ dataclass継承: エラー - {e}")
        return False
    
    return True


def main():
    """メインテスト実行"""
    print("=" * 50)
    print("型定義テスト開始")
    print("=" * 50)
    
    try:
        test_primitives()
        test_entities()
        test_api_types()
        test_sse_types()
        test_field_compatibility()
        test_dataclass_inheritance()
        
        print("\n" + "=" * 50)
        print("✅ すべてのテストが成功しました！")
        print("=" * 50)
        return 0
        
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())