# API構造

## 概要
MAKOTO Visual AIのバックエンドAPIの構造と実装状況をまとめたドキュメント。

## エンドポイント一覧

### chat.py - チャット管理API

#### 基本チャット機能
- `GET /api/chats` - チャット一覧取得（ページネーション対応）
- `GET /api/chats/{chat_id}` - 特定のチャット取得
- `POST /api/chats` - 新規チャット作成または既存チャットへの追加
- `DELETE /api/chats/{chat_id}` - チャット削除

#### ChatGPT連携
- `POST /api/chat/completion` - ChatGPT APIによる単一レスポンス生成
- `POST /api/chat/stream` - ChatGPT APIによるストリーミングレスポンス生成
  - テキスト生成
  - 画像生成モード対応（active_modesに"image"が含まれる場合）
  - Server-Sent Events形式でリアルタイム送信

#### 画像生成
- `POST /api/images/generate` - Azure OpenAI DALL-E 3による画像生成
  - パラメータ：prompt, n, size, quality, output_format
  - レスポンス：生成された画像のURL配列

### library.py - ライブラリ管理API
- `GET /api/libraries` - ライブラリ一覧取得
- `POST /api/libraries` - ライブラリ作成
- `GET /api/libraries/{library_id}` - ライブラリ詳細取得
- `PUT /api/libraries/{library_id}` - ライブラリ更新
- `DELETE /api/libraries/{library_id}` - ライブラリ削除
- `POST /api/libraries/{library_id}/files` - ファイルアップロード
- `DELETE /api/libraries/{library_id}/files/{filename}` - ファイル削除

### task.py - タスク管理API
- `GET /api/tasks` - タスク一覧取得
- `POST /api/tasks` - タスク作成
- `POST /api/tasks/from-template` - テンプレートからタスク作成
- `GET /api/tasks/{task_id}` - タスク詳細取得
- `PUT /api/tasks/{task_id}` - タスク更新
- `DELETE /api/tasks/{task_id}` - タスク削除
- `PUT /api/tasks/{task_id}/archive` - タスクアーカイブ
- `PUT /api/tasks/{task_id}/restore` - タスク復元
- `POST /api/tasks/{task_id}/comments` - コメント追加

### task_template.py - タスクテンプレート管理API
- `GET /api/task-templates` - テンプレート一覧取得
- `POST /api/task-templates` - テンプレート作成
- `GET /api/task-templates/{template_id}` - テンプレート詳細取得
- `PUT /api/task-templates/{template_id}` - テンプレート更新
- `DELETE /api/task-templates/{template_id}` - テンプレート削除

### settings.py - 設定管理API
- `GET /api/settings` - 設定取得
- `PUT /api/settings` - 設定更新

### agent.py - エージェントAI API
- `POST /api/agent/analyze` - プロンプトを分析して最適なモードを判定
  - Webクロール、画像生成、RAGモードの自動判定
  - Function Callingによる厳密な判定
  - 確信度とその理由を含む詳細な分析結果

### websocket.py - WebSocket通信
- `/ws/{client_id}` - WebSocketエンドポイント

## 未実装API（Sample/lambda/から）

### 認証API（要実装）
- `POST /auth/register` - ユーザー新規登録
- `POST /auth/login` - ログイン認証とJWTトークン発行
- `POST /auth/confirm` - メール確認処理
- `POST /auth/resend` - 確認コード再送
- `POST /auth/refresh` - トークンリフレッシュ
- `POST /auth/logout` - ログアウト
- `GET /auth/user` - ユーザー情報取得

### 履歴管理API（要実装）
- `GET /api/chat/history` - チャット履歴取得
  - セッションIDベースの履歴管理
  - 認証必須（JWTトークン検証）
  - ページネーション対応

### メモリ管理API（要実装）
- `GET /api/memory/list` - メモリ一覧取得
- `POST /api/memory/save` - 新規メモリ保存
- `PUT /api/memory/update` - 既存メモリ更新
- `DELETE /api/memory/delete` - メモリ削除
  - ユーザーごとのメモリ（記憶）管理
  - カテゴリ・タグ・重要度管理

### プロファイル管理API（要実装）
- `GET /api/user/profile` - ユーザープロファイル取得
  - Cognitoからユーザー情報取得
  - ユーザー設定（preferences）の管理

### WebSocket拡張（要実装）
- `$connect` - WebSocket接続確立時の認証
- `$disconnect` - WebSocket切断処理
- メッセージアクション拡張：
  - `retrieve_large_message` - S3からの大容量メッセージ取得
  - `ping` - 接続維持用のping/pong

## サービス層

### chat_service.py
- チャットデータの永続化（TinyDB使用）
- メッセージの追加・取得・削除
- チャット履歴の管理

### image_generation_service.py
- Azure OpenAI DALL-E 3統合
- 画像生成リクエストの処理
- Base64画像の保存とURL変換
- 非同期処理対応（aiohttp使用）

### message_processor.py
- メッセージサイズに基づく処理戦略
- 4KB未満: DynamoDB直接保存
- 4KB以上: S3/ローカルストレージ保存
- 128KB上限チェック

### storage_service.py
- 統一ストレージインターフェース
- 開発環境: ローカルファイルシステム
- 本番環境: AWS S3（環境変数で切り替え）

### local_storage_service.py  
- S3互換のローカルストレージ実装
- 開発環境でのファイル保存

### その他のサービス
- library_service.py - ライブラリデータ管理
- task_service.py - タスクデータ管理
- task_template_service.py - テンプレートデータ管理
- settings_service.py - 設定データ管理
- database.py - TinyDBインスタンス管理

## 技術スタック

### バックエンド
- FastAPI - Webフレームワーク
- Uvicorn - ASGIサーバー
- TinyDB - NoSQLデータベース
- Azure OpenAI SDK - ChatGPT/DALL-E 3連携
- aiohttp - 非同期HTTPクライアント（画像生成用）
- Pillow - 画像処理

### 認証・セキュリティ
- CORS設定対応
- 環境変数による機密情報管理

## データフロー

### チャット+画像生成フロー
1. フロントエンドから`/api/chat/stream`にメッセージ送信
2. Azure OpenAI ChatGPTでテキスト生成（ストリーミング）
3. active_modesに"image"が含まれる場合：
   - ユーザーメッセージをプロンプトとして画像生成
   - Azure OpenAI DALL-E 3で画像生成
   - 生成された画像をローカル保存
   - 画像URLをストリーミングで送信
4. チャットデータとメッセージをTinyDBに保存

### ストリーミング形式
```javascript
// テキストチャンク
data: {"content": "こんにちは"}

// 画像生成開始
data: {"generating_image": true}

// 画像生成完了
data: {"images": [{"url": "/uploads/generated_images/xxx.png", "prompt": "...", "created_at": "..."}]}

// エラー
data: {"image_error": "エラーメッセージ"}

// 完了
data: {"done": true, "chat_id": "xxx"}
```

## 環境変数設定

```env
# Azure OpenAI ChatGPT設定
AZURE_OPENAI_ENDPOINT=https://xxx.cognitiveservices.azure.com
AZURE_OPENAI_API_KEY=xxx
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4.1
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure OpenAI DALL-E 3設定
AZURE_OPENAI_IMAGE_ENDPOINT=https://xxx.openai.azure.com/openai/deployments/gpt-image-1/images/generations?api-version=2025-04-01-preview
AZURE_OPENAI_IMAGE_API_KEY=xxx

# モック設定
USE_MOCK_CHATGPT=false
```

## API仕様書

詳細な仕様については、機能別に分割されたAPI仕様書を参照してください：

### 実装済みAPI仕様書
- [API/チャットAPI仕様.md](./API/チャットAPI仕様.md)
- [API/ChatGPT連携API仕様.md](./API/ChatGPT連携API仕様.md)
- [API/画像生成API仕様.md](./API/画像生成API仕様.md)
- [API/エージェントAPI仕様.md](./API/エージェントAPI仕様.md)
- [API/ライブラリ管理API仕様.md](./API/ライブラリ管理API仕様.md)
- [API/タスク管理API仕様.md](./API/タスク管理API仕様.md)

### 未作成API仕様書（要作成）
- タスクテンプレートAPI仕様.md
- 設定管理API仕様.md
- WebSocket通信仕様.md
- 認証API仕様.md
- 履歴管理API仕様.md
- メモリ管理API仕様.md
- プロファイル管理API仕様.md

## 実装優先度

### 高優先度（認証・セキュリティ）
1. **認証API** - ユーザー登録、ログイン、トークン管理
2. **プロファイル管理API** - ユーザー情報管理
3. **WebSocket認証** - 接続時の認証処理

### 中優先度（機能拡張）
1. **履歴管理API** - チャット履歴の永続化と取得
2. **メモリ管理API** - ユーザー固有の記憶管理

### 低優先度（最適化）
1. **WebSocketメッセージ拡張** - 大容量メッセージ、ping/pong

## 更新履歴
- 2025-08-05: 未実装API追加（Sample/lambda/から）
- 2025-07-11: エージェントAI機能追加（プロンプト自動分析）
- 2025-07-11: 大容量メッセージ処理機能追加（128KB上限、S3/ローカルストレージ対応）
- 2025-07-10: 画像生成機能追加（Azure OpenAI gpt-image-1統合）
- 2025-07-10: ストリーミングAPIに画像生成機能統合
- 2025-07-10: aiohttp 3.12.13追加（非同期画像生成用）
- 2025-07-10: API仕様書を機能別に分割