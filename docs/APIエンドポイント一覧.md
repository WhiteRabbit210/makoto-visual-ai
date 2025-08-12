# MAKOTO Visual AI - APIエンドポイント一覧

## 目次
1. [チャットAPI](#チャットapi)
2. [画像生成API](#画像生成api)
3. [エージェントAPI](#エージェントapi)
4. [Webクロール API](#webクロールapi)
5. [ライブラリAPI](#ライブラリapi)
6. [タスクAPI](#タスクapi)
7. [タスクテンプレートAPI](#タスクテンプレートapi)
8. [設定API](#設定api)
9. [WebSocket API](#websocket-api)

---

## チャットAPI

### GET /api/chats
チャット一覧を取得（カーソルベースページネーション）

**パラメータ:**
- `page_size` (int, optional): 1ページあたりの件数（デフォルト: 50、最大: 100）
- `next_key` (string, optional): 次ページ用のカーソルキー
- `tenant_id` (string, optional): テナントID（デフォルト: "default_tenant"）
- `user_id` (string, optional): ユーザーID（デフォルト: "default_user"）

**レスポンス:**
```json
{
  "chats": [ChatRoom],
  "has_more": boolean,
  "next_key": string | null
}
```

### GET /api/chats/{room_id}
特定のチャットを取得

**パラメータ:**
- `room_id` (string): チャットルームID
- `tenant_id` (string, optional): テナントID
- `user_id` (string, optional): ユーザーID
- `page_size` (int, optional): メッセージ取得件数（デフォルト: 50）

**レスポンス:**
```json
{
  "room_id": string,
  "title": string,
  "messages": [Message],
  "created_at": string,
  "updated_at": string
}
```

### POST /api/chats
新規チャット作成またはメッセージ追加

**リクエストボディ:**
```json
{
  "message": string,
  "room_id": string | null
}
```

**レスポンス:**
```json
{
  "room_id": string,
  "message": {...},
  "response": {...}
}
```

### DELETE /api/chats/{room_id}
チャットを削除

**パラメータ:**
- `room_id` (string): チャットルームID
- `tenant_id` (string, optional): テナントID
- `user_id` (string, optional): ユーザーID

### POST /api/chat/completion
ChatGPT補完（非ストリーミング）

**リクエストボディ:**
```json
{
  "messages": [StreamMessage],
  "temperature": number,
  "max_tokens": number,
  "modes": [string]
}
```

### POST /api/chat/stream
ChatGPTストリーミング（Server-Sent Events）

**リクエストボディ:**
```json
{
  "messages": [StreamMessage],
  "room_id": string | null,
  "modes": [string],
  "stream": true,
  "temperature": number,
  "max_tokens": number,
  "search_keywords": [string]
}
```

**レスポンス:** Server-Sent Events
- `data: {"content": "テキスト"}`
- `data: {"generating_image": true}`
- `data: {"images": [...]}`
- `data: {"done": true, "room_id": "..."}`

---

## 画像生成API

### POST /api/images/generate
DALL-E 3で画像を生成

**リクエストボディ:**
```json
{
  "prompt": string,
  "n": number,
  "size": "1024x1024" | "1792x1024" | "1024x1792",
  "quality": "standard" | "hd",
  "output_format": "url" | "base64"
}
```

**レスポンス:**
```json
{
  "success": boolean,
  "images": [{
    "url": string,
    "created_at": string
  }],
  "error": string | null
}
```

---

## エージェントAPI

### POST /api/agent/analyze
プロンプトを分析して適切なモードを推奨

**リクエストボディ:**
```json
{
  "prompt": string,
  "context": [Message]
}
```

**レスポンス:**
```json
{
  "modes": [{
    "type": "chat" | "web" | "image" | "rag",
    "confidence": number,
    "reason": string,
    "search_keywords": [string]
  }],
  "suggested_prompt": string
}
```

### POST /api/agent/status
エージェント実行状態を更新

**リクエストボディ:**
```json
{
  "execution_id": string,
  "agent_type": string,
  "status": string,
  "current_step": number,
  "total_steps": number,
  "message": string
}
```

### GET /api/agent/thinking/{execution_id}
エージェントの思考ログを取得

**パラメータ:**
- `execution_id` (string): 実行ID

---

## Webクロール API

### POST /api/webcrawl/crawl
Webページをクロール

**リクエストボディ:**
```json
{
  "urls": [string],
  "search_keywords": [string],
  "max_results": number,
  "skip_summary": boolean
}
```

**レスポンス:**
```json
{
  "job_id": string,
  "status": "pending" | "processing" | "completed" | "failed",
  "results": [{
    "url": string,
    "title": string,
    "content": string,
    "summary": string
  }]
}
```

### GET /api/webcrawl/status/{job_id}
クロールジョブのステータスを確認

### POST /api/webcrawl/cancel/{job_id}
クロールジョブをキャンセル

### GET /api/webcrawl/jobs
全てのジョブを取得

### POST /api/webcrawl/search
Web検索を実行

**リクエストボディ:**
```json
{
  "query": string,
  "max_results": number,
  "search_type": "general" | "news" | "academic"
}
```

---

## ライブラリAPI

### GET /api/libraries
ライブラリ一覧を取得

**レスポンス:**
```json
[{
  "id": string,
  "name": string,
  "description": string,
  "file_count": number,
  "total_size": number,
  "created_at": string,
  "updated_at": string
}]
```

### GET /api/libraries/{library_id}
ライブラリ詳細を取得（ファイル一覧含む）

### POST /api/libraries
新規ライブラリを作成

**リクエストボディ:**
```json
{
  "name": string,
  "description": string,
  "metadata": {...}
}
```

### PUT /api/libraries/{library_id}
ライブラリ情報を更新

### DELETE /api/libraries/{library_id}
ライブラリとその全ファイルを削除

### POST /api/libraries/{library_id}/files
ファイルをアップロード

**対応形式:** PDF, TXT, DOCX, XLSX, PPTX等
**リクエスト:** multipart/form-data
- `file`: アップロードファイル

### GET /api/libraries/{library_id}/files/{filename}
ファイルをダウンロード

### DELETE /api/libraries/{library_id}/files/{filename}
特定ファイルを削除

### GET /api/libraries/{library_id}/files/{filename}/preview
ファイルプレビュー取得（PDF、画像等）

### GET /api/libraries/{library_id}/files/{filename}/text
ファイルからテキスト抽出（全対応形式）

### POST /api/libraries/{library_id}/embeddings
ライブラリ全体のエンベディングを開始

**レスポンス:**
```json
{
  "job_id": string,
  "status": "pending" | "processing" | "completed" | "failed",
  "total_files": number,
  "processed_files": number
}
```

### GET /api/libraries/{library_id}/embeddings/status
エンベディング処理状況を確認

**レスポンス:**
```json
{
  "status": "idle" | "processing" | "completed" | "failed",
  "total_chunks": number,
  "embedded_chunks": number,
  "last_updated": string,
  "vector_count": number
}
```

### POST /api/libraries/{library_id}/files/{filename}/embeddings
特定ファイルのエンベディングを更新

### DELETE /api/libraries/{library_id}/files/{filename}/embeddings
特定ファイルのエンベディングを削除

### POST /api/libraries/{library_id}/search
ライブラリ内をベクトル検索（RAG用）

**リクエストボディ:**
```json
{
  "query": string,
  "top_k": number,
  "threshold": number
}
```

**レスポンス:**
```json
{
  "results": [{
    "filename": string,
    "chunk": string,
    "score": number,
    "metadata": {...}
  }]
}
```

---

## タスクAPI

### GET /api/tasks
タスク一覧を取得

**パラメータ:**
- `status` (string, optional): "pending" | "running" | "completed" | "failed"
- `category` (string, optional): タスクカテゴリ
- `page` (int, optional): ページ番号
- `per_page` (int, optional): ページあたりの件数

### GET /api/tasks/{task_id}
特定のタスクを取得

### POST /api/tasks
タスクを作成

**リクエストボディ:**
```json
{
  "name": string,
  "category": string,
  "prompt_template": string,
  "parameters": {...},
  "settings": {...}
}
```

### PUT /api/tasks/{task_id}
タスクを更新

### DELETE /api/tasks/{task_id}
タスクを削除

### POST /api/tasks/{task_id}/execute
タスクを実行

**リクエストボディ:**
```json
{
  "parameters": {...},
  "mode": "sync" | "async"
}
```

### GET /api/tasks/{task_id}/executions
タスクの実行履歴を取得

### PUT /api/tasks/{task_id}/visibility
タスクの可視性を更新

**リクエストボディ:**
```json
{
  "visibility": "private" | "team" | "public"
}
```

---

## タスクテンプレートAPI

### GET /api/task-templates
タスクテンプレート一覧を取得

### GET /api/task-templates/{template_id}
特定のテンプレートを取得

### GET /api/task-templates/category/{category}
カテゴリ別テンプレートを取得

---

## 設定API

### GET /api/settings
全設定を取得

### GET /api/settings/{category}
カテゴリ別設定を取得

**カテゴリ:**
- `general`: 一般設定
- `display`: 表示設定
- `api`: API設定
- `privacy`: プライバシー設定

### PUT /api/settings
設定を更新

**リクエストボディ:**
```json
{
  "category": string,
  "settings": {...}
}
```

### POST /api/settings/reset
設定をリセット

---

## WebSocket API

### /ws/chat
リアルタイムチャット通信

**接続方法:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
```

**メッセージ形式:**
```json
{
  "action": "chat",
  "data": {
    "content": string,
    "room_id": string,
    "modes": [string]
  }
}
```

---

## 共通エラーレスポンス

全てのAPIで共通のエラーレスポンス形式：

```json
{
  "error": {
    "code": string,
    "message": string,
    "details": any
  },
  "status": number,
  "timestamp": string
}
```

**HTTPステータスコード:**
- `200`: 成功
- `201`: 作成成功
- `204`: 削除成功
- `400`: リクエスト不正
- `401`: 認証エラー
- `403`: アクセス拒否
- `404`: リソース未検出
- `429`: レート制限
- `500`: サーバーエラー
- `503`: サービス利用不可

---

## 認証・認可

現在の実装では認証機能は未実装ですが、以下のヘッダーで将来対応予定：

```
Authorization: Bearer {token}
X-Tenant-ID: {tenant_id}
X-User-ID: {user_id}
```

---

## レート制限

現在は未実装ですが、以下の制限を予定：
- 通常API: 100リクエスト/分
- チャットストリーミング: 10リクエスト/分
- 画像生成: 5リクエスト/分
- Webクロール: 10リクエスト/分

---

**最終更新日**: 2025年8月12日