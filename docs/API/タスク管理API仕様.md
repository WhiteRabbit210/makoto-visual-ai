# タスク管理API仕様

## 概要
タスクの作成、管理、アーカイブ機能を提供するAPIの仕様書。

## エンドポイント一覧

### 1. タスク一覧取得

**エンドポイント:** `GET /api/tasks`

**説明:** タスクの一覧を取得します。アーカイブされたタスクは含まれません。

**クエリパラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| status | string | - | all | フィルタリング（all, pending, in_progress, completed） |
| priority | string | - | all | 優先度フィルタ（all, high, medium, low） |
| sort | string | - | created_at | ソート項目（created_at, due_date, priority） |
| order | string | - | desc | ソート順（asc, desc） |

**レスポンス例:**
```json
[
  {
    "id": "task-001",
    "title": "API仕様書の作成",
    "description": "画像生成APIの仕様書を作成する",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2025-07-15T17:00:00",
    "assignee": "user-001",
    "tags": ["documentation", "api"],
    "created_at": "2025-07-10T10:00:00",
    "updated_at": "2025-07-10T14:30:00",
    "completed_at": null,
    "archived": false
  },
  {
    "id": "task-002",
    "title": "テストケースの実装",
    "description": "画像生成機能のテストケースを実装",
    "status": "pending",
    "priority": "medium",
    "due_date": "2025-07-20T17:00:00",
    "assignee": null,
    "tags": ["testing", "backend"],
    "created_at": "2025-07-10T11:00:00",
    "updated_at": "2025-07-10T11:00:00",
    "completed_at": null,
    "archived": false
  }
]
```

### 2. タスク詳細取得

**エンドポイント:** `GET /api/tasks/{task_id}`

**説明:** 特定のタスクの詳細情報を取得します。

**パスパラメータ:**
- `task_id`: タスクのID

**レスポンス例:**
```json
{
  "id": "task-001",
  "title": "API仕様書の作成",
  "description": "画像生成APIの仕様書を作成する",
  "status": "in_progress",
  "priority": "high",
  "due_date": "2025-07-15T17:00:00",
  "assignee": "user-001",
  "tags": ["documentation", "api"],
  "created_at": "2025-07-10T10:00:00",
  "updated_at": "2025-07-10T14:30:00",
  "completed_at": null,
  "archived": false,
  "checklist": [
    {
      "id": "check-001",
      "text": "エンドポイント定義",
      "completed": true
    },
    {
      "id": "check-002",
      "text": "パラメータ説明",
      "completed": true
    },
    {
      "id": "check-003",
      "text": "レスポンス例",
      "completed": false
    }
  ],
  "attachments": [],
  "comments": [
    {
      "id": "comment-001",
      "user_id": "user-001",
      "text": "Azure OpenAIの仕様を確認しました",
      "created_at": "2025-07-10T12:00:00"
    }
  ]
}
```

### 3. タスク作成

**エンドポイント:** `POST /api/tasks`

**説明:** 新しいタスクを作成します。

**リクエストボディ:**
```json
{
  "title": "新機能の実装",
  "description": "ユーザー認証機能を実装する",
  "priority": "high",
  "due_date": "2025-07-25T17:00:00",
  "assignee": "user-002",
  "tags": ["feature", "auth"],
  "checklist": [
    {
      "text": "認証フローの設計",
      "completed": false
    },
    {
      "text": "バックエンド実装",
      "completed": false
    }
  ]
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| title | string | ✓ | タスクタイトル |
| description | string | - | タスクの詳細説明 |
| priority | string | - | 優先度（high, medium, low） |
| due_date | string | - | 期限（ISO 8601形式） |
| assignee | string | - | 担当者ID |
| tags | array | - | タグリスト |
| checklist | array | - | チェックリスト |

### 4. タスク更新

**エンドポイント:** `PUT /api/tasks/{task_id}`

**説明:** タスクの情報を更新します。

**パスパラメータ:**
- `task_id`: 更新するタスクのID

**リクエストボディ:**
```json
{
  "title": "更新されたタスクタイトル",
  "status": "completed",
  "priority": "low",
  "checklist": [
    {
      "id": "check-001",
      "text": "認証フローの設計",
      "completed": true
    }
  ]
}
```

### 5. タスク削除

**エンドポイント:** `DELETE /api/tasks/{task_id}`

**説明:** タスクを完全に削除します。

**パスパラメータ:**
- `task_id`: 削除するタスクのID

**レスポンス例:**
```json
{
  "message": "Task deleted successfully"
}
```

### 6. タスクアーカイブ

**エンドポイント:** `PUT /api/tasks/{task_id}/archive`

**説明:** タスクをアーカイブします。アーカイブされたタスクは一覧に表示されません。

**パスパラメータ:**
- `task_id`: アーカイブするタスクのID

**レスポンス例:**
```json
{
  "id": "task-001",
  "title": "API仕様書の作成",
  "archived": true,
  "archived_at": "2025-07-10T16:00:00"
}
```

### 7. タスク復元

**エンドポイント:** `PUT /api/tasks/{task_id}/restore`

**説明:** アーカイブされたタスクを復元します。

**パスパラメータ:**
- `task_id`: 復元するタスクのID

**レスポンス例:**
```json
{
  "id": "task-001",
  "title": "API仕様書の作成",
  "archived": false,
  "restored_at": "2025-07-10T16:30:00"
}
```

### 8. コメント追加

**エンドポイント:** `POST /api/tasks/{task_id}/comments`

**説明:** タスクにコメントを追加します。

**パスパラメータ:**
- `task_id`: コメントを追加するタスクのID

**リクエストボディ:**
```json
{
  "text": "実装が完了しました。レビューをお願いします。",
  "user_id": "user-001"
}
```

## データモデル

### Task
```typescript
interface Task {
  id: string;                // タスクID
  title: string;             // タイトル
  description?: string;      // 説明
  status: TaskStatus;        // ステータス
  priority: TaskPriority;    // 優先度
  due_date?: string;         // 期限
  assignee?: string;         // 担当者ID
  tags: string[];            // タグ
  created_at: string;        // 作成日時
  updated_at: string;        // 更新日時
  completed_at?: string;     // 完了日時
  archived: boolean;         // アーカイブフラグ
  archived_at?: string;      // アーカイブ日時
  checklist?: ChecklistItem[]; // チェックリスト
  attachments?: Attachment[]; // 添付ファイル
  comments?: Comment[];      // コメント
}

type TaskStatus = 'pending' | 'in_progress' | 'completed';
type TaskPriority = 'high' | 'medium' | 'low';
```

### ChecklistItem
```typescript
interface ChecklistItem {
  id: string;          // チェックリストアイテムID
  text: string;        // テキスト
  completed: boolean;  // 完了フラグ
  completed_at?: string; // 完了日時
}
```

### Comment
```typescript
interface Comment {
  id: string;          // コメントID
  user_id: string;     // ユーザーID
  text: string;        // コメント内容
  created_at: string;  // 作成日時
  updated_at?: string; // 更新日時
}
```

## エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `201`: 作成成功
- `400`: 不正なリクエスト
- `404`: タスクが見つからない
- `409`: 競合（既にアーカイブ済みなど）

### エラーレスポンス例

**404 Not Found:**
```json
{
  "detail": "Task not found"
}
```

**409 Conflict:**
```json
{
  "detail": "Task is already archived"
}
```

## タスクテンプレート連携

タスクテンプレートAPIと連携して、定型的なタスクを簡単に作成できます。

**テンプレートからタスク作成:**
```json
POST /api/tasks/from-template

{
  "template_id": "template-001",
  "overrides": {
    "due_date": "2025-07-30T17:00:00",
    "assignee": "user-003"
  }
}
```

## 注意事項

1. **ステータス遷移**: 
   - pending → in_progress → completed
   - 任意のステータスから任意のステータスへ変更可能

2. **自動更新**:
   - `updated_at`は変更時に自動更新
   - `completed_at`はステータスが`completed`になった時に自動設定

3. **アーカイブ**:
   - アーカイブされたタスクは通常の一覧APIでは取得されない
   - 専用のアーカイブ一覧APIで取得可能（今後実装予定）

4. **削除ポリシー**:
   - 削除は物理削除（復元不可）
   - 重要なタスクはアーカイブを推奨