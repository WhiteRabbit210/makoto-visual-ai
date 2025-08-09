# タスク管理API型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [Task](#task)
   - [TaskParameter](#taskparameter)
   - [TaskExecution](#taskexecution)
3. [タスク管理API](#タスク管理api)
   - [GetTasksParams](#gettasksparams)
   - [GetTasksResponse](#gettasksresponse)
   - [CreateTaskRequest](#createtaskrequest)
   - [UpdateTaskRequest](#updatetaskrequest)
4. [タスク実行API](#タスク実行api)
   - [ExecuteTaskRequest](#executetaskrequest)
   - [ExecuteTaskResponse](#executetaskresponse)
   - [TaskExecutionStatus](#taskexecutionstatus)
5. [公開範囲管理](#公開範囲管理)
   - [TaskVisibility](#taskvisibility)
   - [UpdateVisibilityRequest](#updatevisibilityrequest)
6. [エラーレスポンス](#エラーレスポンス)
7. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのタスク管理機能で使用される型定義。プロンプトテンプレートの管理、パラメータ化、実行履歴の管理に関する型を定義。

本ドキュメントは[タスク仕様書](../タスク仕様書.md)に基づいて作成されており、実装時の型定義リファレンスとして使用する。

## 基本型定義

### Task

タスクの基本型定義：

```typescript
interface Task {
  // 基本情報
  task_id: string;                  // タスクID（UUID）
  name: string;                     // タスク名（最大100文字）
  description?: string;             // 説明（最大500文字）
  category: TaskCategory;           // カテゴリー
  tags: string[];                   // タグ（最大10個）
  icon?: string;                    // アイコン（絵文字またはアイコンID）
  
  // プロンプト定義
  prompt_template: string;          // プロンプトテンプレート（最大10000文字）
  system_prompt?: string;           // システムプロンプト（最大2000文字）
  
  // 実行設定
  execution_mode: ExecutionMode;    // 実行モード
  model_settings?: ModelSettings;   // モデル設定
  
  // パラメータ定義
  parameters: TaskParameter[];      // パラメータ定義
  
  // 作成者情報
  created_by: string;               // 作成者ユーザーID
  created_at: string;               // 作成日時（ISO 8601）
  updated_at: string;               // 更新日時
  
  // バージョン管理
  version: number;                  // バージョン番号
  is_latest: boolean;               // 最新バージョンフラグ
  previous_version_id?: string;     // 前バージョンID
  
  // 公開範囲
  visibility: TaskVisibility;       // 公開範囲設定
  
  // ステータス
  status: TaskStatus;               // タスクステータス
  
  // 統計情報
  execution_count: number;          // 実行回数
  last_executed_at?: string;        // 最終実行日時
  average_rating?: number;          // 平均評価（1-5）
}

type TaskCategory = 
  | "text_generation"     // テキスト生成
  | "image_generation"    // 画像生成
  | "data_analysis"       // データ分析
  | "summarization"       // 要約
  | "translation"         // 翻訳
  | "code_generation"     // コード生成
  | "creative_writing"    // クリエイティブライティング
  | "business"            // ビジネス
  | "other";              // その他

type ExecutionMode = 
  | "chat"               // チャットモード
  | "image"              // 画像生成モード
  | "agent"              // エージェントモード
  | "hybrid";            // ハイブリッドモード

type TaskStatus = 
  | "draft"              // 下書き
  | "active"             // アクティブ
  | "deprecated"         // 非推奨
  | "archived";          // アーカイブ済み

interface ModelSettings {
  // LLM設定
  model?: string;                   // モデル名
  temperature?: number;             // 温度（0.0-2.0）
  max_tokens?: number;              // 最大トークン数
  top_p?: number;                   // Top-p（0.0-1.0）
  
  // 画像生成設定
  image_size?: "1024x1024" | "1792x1024" | "1024x1792";
  image_quality?: "standard" | "hd";
  image_style?: "vivid" | "natural";
  image_count?: number;             // 生成枚数（1-10）
  
  // その他
  timeout?: number;                 // タイムアウト（秒）
  retry_count?: number;             // リトライ回数
}
```

### TaskParameter

タスクパラメータの型定義：

```typescript
interface TaskParameter {
  // 基本情報
  parameter_id: string;             // パラメータID
  name: string;                     // パラメータ名（{{name}}で参照）
  label: string;                    // 表示ラベル
  description?: string;             // 説明文
  
  // パラメータ設定
  type: ParameterType;              // パラメータ型
  required: boolean;                // 必須フラグ
  default_value?: any;              // デフォルト値
  
  // 入力制約
  validation?: ParameterValidation; // バリデーション設定
  
  // UI設定
  ui_type: UIType;                  // UI表示タイプ
  placeholder?: string;             // プレースホルダー
  help_text?: string;               // ヘルプテキスト
  display_order: number;            // 表示順序
}

type ParameterType = 
  | "text"               // テキスト
  | "number"             // 数値
  | "boolean"            // 真偽値
  | "date"               // 日付
  | "datetime"           // 日時
  | "select"             // 選択肢
  | "multiselect"        // 複数選択
  | "file"               // ファイル
  | "url";               // URL

interface ParameterValidation {
  // テキスト型
  min_length?: number;              // 最小文字数
  max_length?: number;              // 最大文字数
  pattern?: string;                 // 正規表現パターン
  
  // 数値型
  min_value?: number;               // 最小値
  max_value?: number;               // 最大値
  step?: number;                    // ステップ値
  
  // 選択肢型
  options?: SelectOption[];         // 選択肢リスト
  
  // ファイル型
  allowed_types?: string[];         // 許可するMIMEタイプ
  max_size?: number;                // 最大ファイルサイズ（バイト）
}

interface SelectOption {
  value: string;                    // 値
  label: string;                    // 表示ラベル
  description?: string;             // 説明
}

type UIType = 
  | "text_input"         // テキスト入力
  | "textarea"           // テキストエリア
  | "number_input"       // 数値入力
  | "checkbox"           // チェックボックス
  | "radio"              // ラジオボタン
  | "dropdown"           // ドロップダウン
  | "date_picker"        // 日付ピッカー
  | "file_upload"        // ファイルアップロード
  | "slider";            // スライダー
```

### TaskExecution

タスク実行履歴の型定義：

```typescript
interface TaskExecution {
  // 基本情報
  execution_id: string;             // 実行ID
  task_id: string;                  // タスクID
  task_version: number;             // 実行時のタスクバージョン
  
  // 実行者情報
  executed_by: string;              // 実行者ユーザーID
  executed_at: string;              // 実行日時（ISO 8601）
  
  // 入力パラメータ
  parameters: Record<string, any>;  // 実行時パラメータ値
  
  // 実行結果
  status: TaskExecutionStatus;      // 実行ステータス
  result?: ExecutionResult;         // 実行結果
  error?: ExecutionError;           // エラー情報
  
  // 実行情報
  execution_time_ms: number;        // 実行時間（ミリ秒）
  tokens_used?: number;             // 使用トークン数
  cost?: number;                    // コスト（USD）
  
  // 評価
  rating?: number;                  // 評価（1-5）
  feedback?: string;                // フィードバック
}

interface ExecutionResult {
  // 共通結果
  type: "text" | "image" | "mixed"; // 結果タイプ
  
  // テキスト結果
  text?: string;                    // 生成テキスト
  
  // 画像結果
  images?: Array<{
    url: string;                    // 画像URL
    prompt: string;                 // 使用プロンプト
  }>;
  
  // メタデータ
  metadata?: Record<string, any>;   // その他のメタデータ
}

interface ExecutionError {
  code: string;                     // エラーコード
  message: string;                  // エラーメッセージ
  details?: any;                    // 詳細情報
  occurred_at: string;              // 発生日時
}
```

## タスク管理API

### GetTasksParams

タスク一覧取得パラメータ：

```typescript
interface GetTasksParams {
  // ページング
  page?: number;                    // ページ番号（デフォルト: 1）
  limit?: number;                   // 取得件数（デフォルト: 20、最大: 100）
  
  // フィルタリング
  category?: TaskCategory;          // カテゴリーフィルター
  status?: TaskStatus;              // ステータスフィルター
  execution_mode?: ExecutionMode;   // 実行モードフィルター
  created_by?: string;              // 作成者フィルター
  
  // 検索
  search?: string;                  // 名前・説明検索
  tags?: string[];                  // タグフィルター（OR検索）
  
  // ソート
  sort?: TaskSortField;             // ソートフィールド
  order?: 'asc' | 'desc';           // ソート順（デフォルト: 'desc'）
  
  // 公開範囲
  visibility_type?: 'private' | 'shared' | 'all'; // 表示範囲
}

type TaskSortField = 
  | 'created_at'
  | 'updated_at'
  | 'name'
  | 'execution_count'
  | 'last_executed_at'
  | 'average_rating';
```

### GetTasksResponse

タスク一覧取得レスポンス：

```typescript
interface GetTasksResponse {
  tasks: Task[];                    // タスク一覧
  total: number;                    // 総件数
  page: number;                     // 現在のページ
  limit: number;                    // 取得件数
  total_pages: number;              // 総ページ数
}
```

### CreateTaskRequest

タスク作成リクエスト：

```typescript
interface CreateTaskRequest {
  name: string;                     // タスク名（必須）
  description?: string;             // 説明
  category: TaskCategory;           // カテゴリー（必須）
  tags?: string[];                  // タグ
  icon?: string;                    // アイコン
  
  prompt_template: string;          // プロンプトテンプレート（必須）
  system_prompt?: string;           // システムプロンプト
  
  execution_mode: ExecutionMode;    // 実行モード（必須）
  model_settings?: ModelSettings;   // モデル設定
  
  parameters: TaskParameter[];      // パラメータ定義（必須）
  
  visibility: TaskVisibility;       // 公開範囲（必須）
  
  status?: TaskStatus;              // 初期ステータス（デフォルト: "draft"）
}
```

### UpdateTaskRequest

タスク更新リクエスト：

```typescript
interface UpdateTaskRequest {
  name?: string;                    // タスク名
  description?: string;             // 説明
  category?: TaskCategory;          // カテゴリー
  tags?: string[];                  // タグ
  icon?: string;                    // アイコン
  
  prompt_template?: string;         // プロンプトテンプレート
  system_prompt?: string;           // システムプロンプト
  
  execution_mode?: ExecutionMode;   // 実行モード
  model_settings?: ModelSettings;   // モデル設定
  
  parameters?: TaskParameter[];     // パラメータ定義
  
  visibility?: TaskVisibility;      // 公開範囲
  
  status?: TaskStatus;              // ステータス
  
  // バージョン管理
  create_new_version?: boolean;     // 新バージョン作成フラグ（デフォルト: true）
  version_notes?: string;           // バージョン変更メモ
}
```

## タスク実行API

### ExecuteTaskRequest

タスク実行リクエスト：

```typescript
interface ExecuteTaskRequest {
  parameters: Record<string, any>;  // パラメータ名と値のマップ（必須）
  
  options?: {
    save_history?: boolean;         // 履歴保存（デフォルト: true）
    return_metadata?: boolean;      // メタデータ返却（デフォルト: false）
    override_settings?: {           // 設定上書き
      model?: string;
      temperature?: number;
      max_tokens?: number;
    };
  };
}
```

### ExecuteTaskResponse

タスク実行レスポンス：

```typescript
interface ExecuteTaskResponse {
  execution_id: string;             // 実行ID
  status: TaskExecutionStatus;      // 実行ステータス
  
  result?: ExecutionResult;         // 実行結果（完了時）
  
  metadata?: {
    execution_time_ms: number;     // 実行時間
    tokens_used?: number;           // 使用トークン数
    cost?: number;                  // コスト
    model_used?: string;            // 使用モデル
  };
  
  stream_url?: string;              // ストリーミングURL（SSE用）
}
```

### TaskExecutionStatus

タスク実行ステータス：

```typescript
type TaskExecutionStatus = 
  | "pending"            // 実行待ち
  | "running"            // 実行中
  | "completed"          // 完了
  | "failed"             // 失敗
  | "cancelled"          // キャンセル
  | "timeout";           // タイムアウト
```

## 公開範囲管理

### TaskVisibility

タスク公開範囲（ライブラリと同一仕様）：

```typescript
interface TaskVisibility {
  // 公開タイプ
  visibility_type: VisibilityType;
  
  // 部署指定（AND条件）
  departments?: string[];           // 部署名リスト
  
  // 役職指定（AND条件）
  roles?: string[];                 // 役職名リスト
  
  // ユーザー指定（OR条件）
  users?: string[];                 // ユーザーIDリスト
}

type VisibilityType = 
  | "private"       // 作成者のみ
  | "specific"      // 特定の条件指定
  | "tenant";       // テナント全体
```

### UpdateVisibilityRequest

公開範囲更新リクエスト：

```typescript
interface UpdateVisibilityRequest {
  visibility: TaskVisibility;       // 新しい公開範囲設定
  
  notify_users?: boolean;           // 変更通知（デフォルト: false）
  notification_message?: string;    // 通知メッセージ
}
```

## エラーレスポンス

タスク管理特有のエラーレスポンス：

```typescript
interface TaskErrorResponse {
  error: {
    code: TaskErrorCode;            // エラーコード
    message: string;                // エラーメッセージ
    details?: {
      field?: string;               // エラーフィールド
      validation_errors?: Array<{  // バリデーションエラー
        parameter: string;
        message: string;
      }>;
      missing_parameters?: string[]; // 不足パラメータ
    };
  };
  status: number;                   // HTTPステータスコード
  request_id: string;               // リクエストID
}

enum TaskErrorCode {
  // タスク関連
  TASK_NOT_FOUND = 'TASK001',
  TASK_ACCESS_DENIED = 'TASK002',
  TASK_ALREADY_EXISTS = 'TASK003',
  
  // パラメータ関連
  INVALID_PARAMETERS = 'TASK101',
  MISSING_REQUIRED_PARAMETER = 'TASK102',
  PARAMETER_VALIDATION_FAILED = 'TASK103',
  
  // 実行関連
  EXECUTION_FAILED = 'TASK201',
  EXECUTION_TIMEOUT = 'TASK202',
  EXECUTION_RATE_LIMIT = 'TASK203',
  
  // テンプレート関連
  INVALID_TEMPLATE = 'TASK301',
  TEMPLATE_VARIABLE_MISSING = 'TASK302',
  
  // その他
  INVALID_REQUEST = 'TASK401',
  INTERNAL_ERROR = 'TASK500'
}
```

## 更新履歴

- 2025-08-06: 初版作成
  - タスク仕様書に基づく型定義
  - プロンプトテンプレート機能の型定義
  - パラメータ化とバリデーション機能
  - ライブラリと同一の公開範囲設定