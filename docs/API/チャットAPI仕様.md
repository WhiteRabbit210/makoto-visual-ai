# チャットAPI仕様

## 概要
MAKOTO Visual AIのチャット関連APIの詳細仕様書。

## エンドポイント一覧

### 1. チャット一覧取得

**エンドポイント:** `GET /api/chats`

**説明:** 保存されているチャット一覧をカーソルベースページネーションで取得します。

**パラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| page_size | integer | - | 50 | 1ページあたりの件数（最大100） |
| next_key | string | - | null | 次ページ用のカーソルキー |
| tenant_id | string | - | "default_tenant" | テナントID |
| user_id | string | - | "default_user" | ユーザーID |

**レスポンス例:**
```json
{
  "chats": [
    {
      "id": "86474bdb-3dbb-44b2-8b20-4d78c2c230fd",
      "title": "美しい蝶のイラストを生成して",
      "created_at": "2025-07-10T10:00:00",
      "updated_at": "2025-07-10T10:30:00",
      "last_message": "承知しました。美しい蝶のイラストを生成します。"
    }
  ],
  "has_more": true,
  "next_key": "CHAT#2025-07-10T09:00:00Z#uuid"
}
```

### 2. チャット詳細取得

**エンドポイント:** `GET /api/chats/{room_id}`

**説明:** 特定のチャットの詳細情報とメッセージ履歴を取得します。

**パスパラメータ:**
- `room_id`: チャットルームID

**レスポンス例:**
```json
{
  "id": "86474bdb-3dbb-44b2-8b20-4d78c2c230fd",
  "title": "美しい蝶のイラストを生成して",
  "created_at": "2025-07-10T10:00:00",
  "updated_at": "2025-07-10T10:30:00",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "美しい蝶のイラストを生成してください",
      "timestamp": "2025-07-10T10:00:00"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "承知しました。美しい蝶のイラストを生成します。",
      "timestamp": "2025-07-10T10:00:05",
      "images": [
        {
          "url": "/uploads/generated_images/美しい蝶_abc123.png",
          "prompt": "美しい蝶のイラスト",
          "created_at": "2025-07-10T10:00:10"
        }
      ]
    }
  ]
}
```

### 3. チャット作成

**エンドポイント:** `POST /api/chats`

**説明:** 新規チャットを作成、または既存チャットにメッセージを追加します。
※ このエンドポイントはモックレスポンスを返します。実際のAI応答にはストリーミングAPIを使用してください。

**リクエストボディ:**
```json
{
  "message": "新しいチャットを始めます",
  "chat_id": "optional-existing-chat-id"
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| message | string | ✓ | ユーザーのメッセージ |
| chat_id | string | - | 既存チャットのID（省略時は新規作成） |

**レスポンス例:**
```json
{
  "chat_id": "new-chat-123",
  "message": {
    "id": "msg-1",
    "role": "user",
    "content": "新しいチャットを始めます",
    "timestamp": "2025-07-10T10:00:00"
  },
  "response": {
    "id": "msg-2",
    "role": "assistant",
    "content": "これは'新しいチャットを始めます'に対するモック応答です。実際の実装では、Azure OpenAIを使用します。",
    "timestamp": "2025-07-10T10:00:01"
  }
}
```

### 4. チャット削除

**エンドポイント:** `DELETE /api/chats/{chat_id}`

**説明:** 指定したチャットとその全メッセージを削除します。

**パスパラメータ:**
- `chat_id`: 削除するチャットのUUID

**レスポンス例:**
```json
{
  "message": "Chat deleted successfully"
}
```

**エラーレスポンス (404):**
```json
{
  "detail": "Chat not found"
}
```

## データモデル

### Chat
```typescript
interface Chat {
  id: string;           // UUID
  title: string;        // チャットタイトル
  created_at: string;   // 作成日時（ISO 8601形式）
  updated_at: string;   // 更新日時（ISO 8601形式）
  last_message?: string; // 最後のメッセージ（省略可）
  messages?: Message[]; // メッセージ配列（詳細取得時のみ）
}
```

### Message
```typescript
interface Message {
  id: string;          // メッセージID
  role: 'user' | 'assistant'; // 送信者の役割
  content: string;     // メッセージ内容
  timestamp: string;   // 送信日時
  images?: Image[];    // 生成された画像（assistantのみ）
}
```

### Image
```typescript
interface Image {
  url: string;         // 画像のURL
  prompt?: string;     // 生成時のプロンプト
  created_at?: string; // 生成日時
}
```

## 注意事項

1. **チャット作成API (`POST /api/chats`)** はモック応答を返します。実際のAI応答が必要な場合は、ChatGPT連携APIを使用してください。

2. **チャットIDの形式**: UUIDv4形式（例: `86474bdb-3dbb-44b2-8b20-4d78c2c230fd`）

3. **タイムスタンプ形式**: 
   - バックエンド: ISO 8601形式（例: `2025-07-10T10:00:00`）
   - フロントエンド表示: 日本語ローカライズ（例: `2025/07/10 10:00:00`）

4. **ページネーション**: 
   - デフォルトで20件ずつ取得
   - `has_more`フラグで次ページの有無を判定

5. **データ永続化**: TinyDBを使用してローカルファイルに保存