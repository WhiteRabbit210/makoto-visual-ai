# チャットAPIページネーション仕様

## 目次
1. [概要](#概要)
2. [背景と目的](#背景と目的)
3. [API仕様](#api仕様)
4. [実装詳細](#実装詳細)
5. [フロントエンド実装例](#フロントエンド実装例)
6. [パフォーマンス最適化](#パフォーマンス最適化)

## 概要

チャットAPIのページネーション機能により、大量のチャットルームを効率的に取得できるようになりました。UIでのスクロールに合わせた遅延読み込みに対応し、50件ずつのデータ取得が可能です。

## 背景と目的

### 要件
- ユーザーが数百〜数千のチャットルームを持つ可能性がある
- UIでは初期表示は50件程度で十分
- スクロールに応じて追加データを遅延読み込み
- パフォーマンスとUXの両立

### 解決策
- KVM（DynamoDB/CosmosDB）を使用した高速メタデータ取得
- カーソルベースのページネーション
- `room_id`での統一的な識別子管理

## API仕様

### チャット一覧取得API

#### エンドポイント
```
GET /api/chats
```

#### リクエストパラメータ
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|----------|------|------|------------|------|
| limit | int | No | 50 | 取得件数（最大100） |
| next_key | string | No | null | 次ページ用のキー |
| tenant_id | string | No | "default_tenant" | テナントID |
| user_id | string | No | "default_user" | ユーザーID |

#### レスポンス
```json
{
  "chats": [
    {
      "id": "room_abc123",
      "title": "ミツイワ社長について",
      "created_at": "2025-08-12T10:00:00Z",
      "updated_at": "2025-08-12T12:34:56Z",
      "message_count": 42,
      "last_message": "質問ありがとうございます...",
      "last_message_time": "2025-08-12T12:34:56Z",
      "last_message_role": "assistant",
      "unread_count": 0,
      "status": "active"
    }
  ],
  "has_more": true,
  "next_key": "CHAT#room_xyz789",
  "total_count": 50
}
```

### 使用例

#### 初回リクエスト
```bash
curl -X GET "http://localhost:8000/api/chats?limit=50"
```

#### 2ページ目のリクエスト
```bash
curl -X GET "http://localhost:8000/api/chats?limit=50&next_key=CHAT%23room_xyz789"
```

## 実装詳細

### バックエンド実装

#### ChatService
```python
@staticmethod
async def get_all_chats(
    tenant_id: str = "default_tenant", 
    user_id: str = "default_user", 
    limit: int = 50, 
    last_evaluated_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    KVMから高速にチャットメタデータを取得
    """
    pk = f"TENANT#{tenant_id}#USER#{user_id}"
    sk_prefix = "CHAT#"
    
    # ページネーション対応のクエリ
    chat_items = await kvm_service.query(
        pk=pk,
        sk_prefix=sk_prefix,
        limit=limit,
        scan_forward=False,  # 新しい順
        last_evaluated_key=last_evaluated_key
    )
    
    # レスポンス構築
    return {
        'chats': formatted_chats,
        'has_more': len(chat_items) == limit,
        'next_key': last_item.get('SK') if has_more else None,
        'total_count': len(formatted_chats)
    }
```

### KVMサービス
```python
async def query(
    self, 
    pk: str, 
    sk_prefix: str = None, 
    limit: int = 100,
    scan_forward: bool = False,
    last_evaluated_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    DynamoDB/CosmosDBから効率的にデータ取得
    """
    # カーソルベースのページネーション実装
    # last_evaluated_keyから次のページを取得
```

## フロントエンド実装例

### React/Next.jsでの無限スクロール実装

```typescript
import { useState, useEffect, useCallback } from 'react';
import { useInView } from 'react-intersection-observer';

interface Chat {
  id: string;
  title: string;
  last_message: string;
  updated_at: string;
}

interface ChatsResponse {
  chats: Chat[];
  has_more: boolean;
  next_key: string | null;
  total_count: number;
}

export function ChatList() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [nextKey, setNextKey] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  
  // 無限スクロール用のIntersection Observer
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '100px',
  });

  // チャット取得関数
  const loadMoreChats = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: '50',
        ...(nextKey && { next_key: nextKey }),
      });
      
      const response = await fetch(`/api/chats?${params}`);
      const data: ChatsResponse = await response.json();
      
      setChats(prev => [...prev, ...data.chats]);
      setNextKey(data.next_key);
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setLoading(false);
    }
  }, [nextKey, hasMore, loading]);

  // スクロール位置に応じて追加読み込み
  useEffect(() => {
    if (inView) {
      loadMoreChats();
    }
  }, [inView, loadMoreChats]);

  // 初回読み込み
  useEffect(() => {
    loadMoreChats();
  }, []);

  return (
    <div className="chat-list">
      {chats.map(chat => (
        <ChatItem key={chat.id} chat={chat} />
      ))}
      
      {/* 無限スクロールのトリガー */}
      {hasMore && (
        <div ref={ref} className="loading-trigger">
          {loading && <Spinner />}
        </div>
      )}
    </div>
  );
}
```

### Vue.jsでの実装例

```vue
<template>
  <div class="chat-list" @scroll="handleScroll">
    <chat-item 
      v-for="chat in chats" 
      :key="chat.id" 
      :chat="chat" 
    />
    <div v-if="loading" class="loading">読み込み中...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const chats = ref<Chat[]>([]);
const nextKey = ref<string | null>(null);
const hasMore = ref(true);
const loading = ref(false);

async function loadMoreChats() {
  if (loading.value || !hasMore.value) return;
  
  loading.value = true;
  try {
    const params = new URLSearchParams({
      limit: '50',
      ...(nextKey.value && { next_key: nextKey.value }),
    });
    
    const response = await fetch(`/api/chats?${params}`);
    const data = await response.json();
    
    chats.value.push(...data.chats);
    nextKey.value = data.next_key;
    hasMore.value = data.has_more;
  } finally {
    loading.value = false;
  }
}

function handleScroll(event: Event) {
  const element = event.target as HTMLElement;
  const bottom = element.scrollHeight - element.scrollTop === element.clientHeight;
  
  if (bottom && hasMore.value) {
    loadMoreChats();
  }
}

onMounted(() => {
  loadMoreChats();
});
</script>
```

## パフォーマンス最適化

### 1. KVMによる高速化
- DynamoDB/CosmosDBでメタデータ管理
- インデックスによる高速クエリ
- 実データはBlobStorage/S3に保存

### 2. キャッシング戦略
```python
# Redis/ElastiCacheによるキャッシュ
cache_key = f"chats:{tenant_id}:{user_id}:page:{page_num}"
cached_data = await redis.get(cache_key)
if cached_data:
    return json.loads(cached_data)
```

### 3. レスポンス最適化
- 必要最小限のフィールドのみ返す
- last_messageは50文字のプレビューのみ
- 詳細情報は個別APIで取得

### 4. 並列処理
```python
# 複数のメタデータを並列取得
tasks = [
    get_chat_metadata(room_id) 
    for room_id in room_ids
]
results = await asyncio.gather(*tasks)
```

## 移行ガイド

### 既存APIからの移行

#### Before（chat_id使用）
```javascript
// 旧API
fetch(`/api/chats/${chatId}`)
```

#### After（room_id使用）
```javascript
// 新API
fetch(`/api/chats/${roomId}`)
```

### 互換性の維持
レスポンスの`chat_id`フィールドは互換性のため残していますが、内部的には`room_id`を使用：

```json
{
  "chat_id": "room_abc123",  // 互換性のため
  "id": "room_abc123",        // 推奨
  ...
}
```

## まとめ

### 実装済み機能
- ✅ 50件ずつのページネーション
- ✅ カーソルベースの効率的な取得
- ✅ KVMによる高速メタデータ取得
- ✅ room_idへの統一
- ✅ 無限スクロール対応

### 今後の拡張予定
- 検索機能の追加
- リアルタイム更新（WebSocket）
- キャッシュ戦略の強化
- 読み込み済みデータの差分更新

---

**作成者**: Claude  
**作成日**: 2025年8月12日  
**バージョン**: 1.0.0