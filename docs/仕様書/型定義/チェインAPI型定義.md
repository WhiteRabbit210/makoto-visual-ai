# チェインAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [Chain](#chain)
   - [ChainStep](#chainstep)
   - [ChainParameter](#chainparameter)
   - [ChainExecution](#chainexecution)
3. [制御フロー型定義](#制御フロー型定義)
   - [ControlFlow](#controlflow)
   - [ExecutionCondition](#executioncondition)
   - [ErrorHandling](#errorhandling)
4. [データマッピング型定義](#データマッピング型定義)
   - [InputMapping](#inputmapping)
   - [OutputMapping](#outputmapping)
   - [DataSource](#datasource)
5. [実行管理型定義](#実行管理型定義)
   - [ExecutionConfig](#executionconfig)
   - [ExecutionStatus](#executionstatus)
   - [ExecutionResult](#executionresult)
6. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [チェイン作成](#チェイン作成)
   - [チェイン実行](#チェイン実行)
   - [実行状態取得](#実行状態取得)
   - [チェイン管理](#チェイン管理)
7. [公開範囲型定義](#公開範囲型定義)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのチェイン機能で使用される型定義。複数のタスクを連結して複雑なワークフローを構築するための構造を定義する。

## 基本型定義

### Chain

チェインの基本構造：

```typescript
interface Chain {
  // 基本情報
  chain_id: string;                       // チェインID（UUID）
  name: string;                          // チェイン名（最大100文字）
  description?: string;                   // 説明（最大500文字）
  category: ChainCategory;                // カテゴリー
  tags: string[];                        // タグ（最大10個）
  icon?: string;                         // アイコンURL
  
  // ステップ定義
  steps: ChainStep[];                    // ステップ配列
  
  // 入力パラメータ定義
  input_parameters: ChainParameter[];    // チェイン全体の入力パラメータ
  
  // 出力定義
  output_mapping: OutputMapping;          // 最終出力のマッピング
  
  // 実行設定
  execution_config: ExecutionConfig;      // 実行設定
  
  // 作成者情報
  created_by: string;                    // 作成者ユーザーID
  created_at: string;                    // 作成日時（ISO 8601）
  updated_at: string;                    // 更新日時（ISO 8601）
  
  // バージョン管理
  version: number;                       // バージョン番号
  is_latest: boolean;                   // 最新バージョンフラグ
  
  // 公開範囲（タスク・ライブラリと同一仕様）
  visibility: ChainVisibility;           // 公開範囲設定
  
  // ステータス
  status: ChainStatus;                   // チェインステータス
  
  // 統計情報
  execution_count: number;               // 実行回数
  average_execution_time?: number;       // 平均実行時間（秒）
  success_rate?: number;                 // 成功率（%）
  last_executed_at?: string;            // 最終実行日時
}

// チェインカテゴリー
type ChainCategory = 
  | "data_processing"      // データ処理
  | "content_creation"     // コンテンツ作成
  | "analysis"             // 分析
  | "automation"           // 自動化
  | "integration"          // 統合処理
  | "other";               // その他

// チェインステータス
type ChainStatus = 
  | "draft"                // 下書き
  | "active"               // アクティブ
  | "testing"              // テスト中
  | "deprecated"           // 非推奨
  | "archived";            // アーカイブ済み
```

### ChainStep

チェインステップの定義：

```typescript
interface ChainStep {
  // 基本情報
  step_id: string;                       // ステップID
  name: string;                          // ステップ名
  description?: string;                  // 説明
  
  // 実行タイプ
  type: StepType;                        // ステップタイプ
  
  // タスク実行（type="task"の場合）
  task_config?: {
    task_id: string;                     // 実行するタスクID
    task_version?: number;               // タスクバージョン（省略時は最新）
  };
  
  // 制御フロー設定
  control_flow?: ControlFlow;            // 制御フロー設定
  
  // データマッピング
  input_mapping: InputMapping;           // 入力マッピング
  output_mapping: OutputMapping;         // 出力マッピング
  
  // 実行条件
  condition?: ExecutionCondition;        // 実行条件
  
  // エラーハンドリング
  error_handling?: ErrorHandling;        // エラー処理設定
  
  // 実行設定
  timeout?: number;                      // タイムアウト（秒）
  retry_count?: number;                  // リトライ回数
  retry_delay?: number;                  // リトライ間隔（秒）
  
  // 依存関係
  depends_on?: string[];                 // 依存するステップID配列
  
  // UI設定
  position?: {                          // ビジュアルエディタでの位置
    x: number;
    y: number;
  };
}

// ステップタイプ
type StepType = 
  | "task"                 // タスク実行
  | "condition"            // 条件分岐
  | "loop"                 // ループ
  | "parallel"             // 並列実行
  | "wait"                 // 待機
  | "transform"            // データ変換
  | "aggregate"            // データ集約
  | "output";              // 出力
```

### ChainParameter

チェインパラメータの定義：

```typescript
interface ChainParameter {
  name: string;                          // パラメータ名
  type: ParameterType;                   // パラメータ型
  description?: string;                  // 説明
  required: boolean;                     // 必須フラグ
  default_value?: any;                   // デフォルト値
  
  // バリデーション
  validation?: {
    min?: number;                        // 最小値（数値型）
    max?: number;                        // 最大値（数値型）
    min_length?: number;                 // 最小文字数（文字列型）
    max_length?: number;                 // 最大文字数（文字列型）
    pattern?: string;                    // 正規表現パターン
    enum?: any[];                        // 選択肢
  };
  
  // UI設定
  ui_config?: {
    label?: string;                      // 表示ラベル
    placeholder?: string;                // プレースホルダー
    help_text?: string;                  // ヘルプテキスト
    input_type?: string;                 // 入力タイプ（text, number, select等）
  };
}

// パラメータ型
type ParameterType = 
  | "string"
  | "number"
  | "boolean"
  | "array"
  | "object"
  | "date"
  | "file";
```

### ChainExecution

チェイン実行情報：

```typescript
interface ChainExecution {
  // 実行情報
  execution_id: string;                  // 実行ID
  chain_id: string;                      // チェインID
  chain_version: number;                 // チェインバージョン
  
  // 実行者情報
  executed_by: string;                   // 実行者ユーザーID
  tenant_id: string;                     // テナントID
  
  // 入力パラメータ
  input_parameters: Record<string, any>; // 入力パラメータ値
  
  // 実行状態
  status: ExecutionStatus;               // 実行ステータス
  current_step_id?: string;              // 現在実行中のステップID
  
  // 実行結果
  output?: any;                          // 最終出力
  error?: ExecutionError;                // エラー情報
  
  // ステップ実行情報
  step_executions: StepExecution[];      // ステップ実行情報配列
  
  // タイミング
  started_at: string;                    // 開始日時
  completed_at?: string;                 // 完了日時
  execution_time_ms?: number;            // 実行時間（ミリ秒）
  
  // メタデータ
  metadata?: Record<string, any>;        // カスタムメタデータ
}

// ステップ実行情報
interface StepExecution {
  step_id: string;                       // ステップID
  status: ExecutionStatus;               // ステータス
  started_at?: string;                   // 開始日時
  completed_at?: string;                 // 完了日時
  duration_ms?: number;                  // 実行時間（ミリ秒）
  
  input?: any;                           // 入力データ
  output?: any;                          // 出力データ
  error?: ExecutionError;                // エラー情報
  
  retry_count?: number;                  // リトライ回数
}
```

## 制御フロー型定義

### ControlFlow

制御フローの定義：

```typescript
interface ControlFlow {
  type: "sequential" | "conditional" | "loop" | "parallel";
  
  // 条件分岐
  conditional?: {
    conditions: Array<{
      expression: string;                // 条件式
      next_step_id: string;              // 次のステップID
    }>;
    default_step_id?: string;            // デフォルトステップID
  };
  
  // ループ処理
  loop?: {
    type: "for" | "while" | "foreach";
    
    // forループ
    for_config?: {
      start: number;                     // 開始値
      end: number;                       // 終了値
      step: number;                      // ステップ値
    };
    
    // whileループ
    while_config?: {
      condition: string;                 // 継続条件式
      max_iterations?: number;           // 最大繰り返し回数
    };
    
    // foreachループ
    foreach_config?: {
      items_source: DataSource;          // 配列データソース
      item_variable_name: string;        // アイテム変数名
      index_variable_name?: string;      // インデックス変数名
    };
    
    // ループ本体
    loop_steps: string[];                // ループ内のステップID配列
  };
  
  // 並列実行
  parallel?: {
    branches: Array<{
      branch_id: string;                 // ブランチID
      step_ids: string[];                // ステップID配列
    }>;
    wait_all: boolean;                   // 全ブランチ完了待機
    aggregation_method?: AggregationMethod; // 結果の集約方法
  };
}

// 集約方法
type AggregationMethod = 
  | "merge_object"         // オブジェクトマージ
  | "concat_array"         // 配列結合
  | "first_completed"      // 最初に完了した結果
  | "custom";              // カスタム集約
```

### ExecutionCondition

実行条件の定義：

```typescript
interface ExecutionCondition {
  type: "expression" | "script" | "rule";
  
  // 式評価
  expression?: string;                   // 条件式（例: "${input.value} > 100"）
  
  // スクリプト評価
  script?: {
    language: "javascript" | "python";   // スクリプト言語
    code: string;                        // スクリプトコード
  };
  
  // ルールベース評価
  rule?: {
    operator: "and" | "or" | "not";     // 論理演算子
    conditions: Array<{
      field: string;                     // フィールドパス
      operator: ComparisonOperator;      // 比較演算子
      value: any;                        // 比較値
    }>;
  };
}

// 比較演算子
type ComparisonOperator = 
  | "eq"                   // 等しい
  | "ne"                   // 等しくない
  | "gt"                   // より大きい
  | "gte"                  // 以上
  | "lt"                   // より小さい
  | "lte"                  // 以下
  | "in"                   // 含まれる
  | "not_in"               // 含まれない
  | "contains"             // 含む
  | "starts_with"          // で始まる
  | "ends_with"            // で終わる
  | "matches";             // 正規表現マッチ
```

### ErrorHandling

エラーハンドリングの定義：

```typescript
interface ErrorHandling {
  strategy: ErrorStrategy;               // エラー戦略
  
  // リトライ設定
  retry?: {
    max_attempts: number;                // 最大試行回数
    delay_ms: number;                    // リトライ間隔（ミリ秒）
    backoff_multiplier?: number;         // バックオフ乗数
    retry_on?: string[];                 // リトライ対象エラーコード
  };
  
  // フォールバック
  fallback?: {
    type: "step" | "value" | "skip";
    fallback_step_id?: string;          // フォールバックステップID
    fallback_value?: any;                // フォールバック値
  };
  
  // エラー通知
  notification?: {
    enabled: boolean;                    // 通知有効化
    channels: NotificationChannel[];     // 通知チャンネル
    severity_threshold?: ErrorSeverity;  // 通知する最低重要度
  };
  
  // エラーログ
  logging?: {
    enabled: boolean;                    // ログ有効化
    include_details: boolean;            // 詳細情報を含める
  };
}

// エラー戦略
type ErrorStrategy = 
  | "fail_fast"            // 即座に失敗
  | "retry"                // リトライ
  | "fallback"             // フォールバック
  | "continue"             // 継続
  | "compensate";          // 補償処理

// 通知チャンネル
type NotificationChannel = 
  | "email"
  | "slack"
  | "teams"
  | "webhook";

// エラー重要度
type ErrorSeverity = 
  | "low"
  | "medium"
  | "high"
  | "critical";
```

## データマッピング型定義

### InputMapping

入力マッピングの定義：

```typescript
interface InputMapping {
  // マッピングタイプ
  type: "direct" | "template" | "transform";
  
  // 直接マッピング
  direct_mappings?: Array<{
    target_param: string;                // 対象パラメータ名
    source: DataSource;                  // データソース
  }>;
  
  // テンプレートマッピング
  template?: string;                     // テンプレート文字列（例: "Hello ${name}"）
  
  // 変換マッピング
  transform?: {
    function: TransformFunction;         // 変換関数
    parameters: Record<string, any>;     // 変換パラメータ
  };
}
```

### OutputMapping

出力マッピングの定義：

```typescript
interface OutputMapping {
  // マッピングタイプ
  type: "direct" | "extract" | "transform";
  
  // 出力フィールド定義
  fields?: Array<{
    name: string;                        // フィールド名
    source_path: string;                 // ソースパス（例: "result.data[0].value"）
    required?: boolean;                  // 必須フラグ
  }>;
  
  // データ抽出
  extract?: {
    type: "json_path" | "regex" | "xpath";
    expression: string;                  // 抽出式
  };
  
  // 出力変換
  transform?: {
    function: TransformFunction;         // 変換関数
    parameters: Record<string, any>;     // 変換パラメータ
  };
}
```

### DataSource

データソースの定義：

```typescript
interface DataSource {
  type: "chain_input" | "step_output" | "constant" | "variable" | "context";
  
  // チェイン入力参照
  chain_input_name?: string;             // チェイン入力パラメータ名
  
  // ステップ出力参照
  step_id?: string;                      // ソースステップID
  output_path?: string;                  // 出力パス（例: "result.text"）
  
  // 定数値
  constant_value?: any;                  // 定数値
  
  // 変数参照
  variable_name?: string;                // 変数名
  
  // コンテキスト参照
  context_key?: string;                  // コンテキストキー（user_id, tenant_id等）
}

// 変換関数
type TransformFunction = 
  | "json_extract"         // JSON抽出
  | "text_split"           // テキスト分割
  | "text_join"            // テキスト結合
  | "array_map"            // 配列マッピング
  | "array_filter"         // 配列フィルタ
  | "array_reduce"         // 配列集約
  | "date_format"          // 日付フォーマット
  | "number_format"        // 数値フォーマット
  | "custom";              // カスタム関数
```

## 実行管理型定義

### ExecutionConfig

実行設定の定義：

```typescript
interface ExecutionConfig {
  // 実行モード
  mode: ExecutionMode;                   // 実行モード
  
  // タイムアウト設定
  timeout?: {
    total_timeout_seconds?: number;      // 全体タイムアウト（秒）
    step_timeout_seconds?: number;       // ステップごとのタイムアウト（秒）
  };
  
  // 並列実行設定
  parallelism?: {
    max_concurrent_steps?: number;       // 最大同時実行ステップ数
    max_concurrent_iterations?: number;  // ループの最大同時実行数
  };
  
  // リソース制限
  resource_limits?: {
    max_memory_mb?: number;              // 最大メモリ使用量（MB）
    max_cpu_percent?: number;            // 最大CPU使用率（%）
  };
  
  // スケジュール実行
  schedule?: {
    cron_expression?: string;            // Cron式
    timezone?: string;                   // タイムゾーン
    start_date?: string;                 // 開始日
    end_date?: string;                   // 終了日
  };
  
  // トリガー設定
  triggers?: Array<{
    type: TriggerType;                   // トリガータイプ
    config: Record<string, any>;         // トリガー設定
  }>;
  
  // ログ設定
  logging?: {
    level: LogLevel;                     // ログレベル
    include_input_output?: boolean;      // 入出力を含める
  };
}

// 実行モード
type ExecutionMode = 
  | "immediate"            // 即時実行
  | "scheduled"            // スケジュール実行
  | "triggered"            // トリガー実行
  | "manual";              // 手動実行

// トリガータイプ
type TriggerType = 
  | "webhook"              // Webhook
  | "file_upload"          // ファイルアップロード
  | "event"                // イベント
  | "api_call";            // API呼び出し

// ログレベル
type LogLevel = 
  | "debug"
  | "info"
  | "warning"
  | "error";
```

### ExecutionStatus

実行ステータス：

```typescript
enum ExecutionStatus {
  PENDING = "pending",           // 待機中
  QUEUED = "queued",            // キュー待ち
  RUNNING = "running",          // 実行中
  PAUSED = "paused",            // 一時停止
  COMPLETED = "completed",      // 完了
  FAILED = "failed",            // 失敗
  CANCELLED = "cancelled",      // キャンセル
  TIMEOUT = "timeout"           // タイムアウト
}
```

### ExecutionResult

実行結果：

```typescript
interface ExecutionResult {
  execution_id: string;                  // 実行ID
  status: ExecutionStatus;               // 最終ステータス
  
  // 成功時
  output?: any;                          // 出力データ
  
  // 失敗時
  error?: ExecutionError;                // エラー情報
  
  // 統計情報
  statistics: {
    total_steps: number;                 // 総ステップ数
    completed_steps: number;             // 完了ステップ数
    failed_steps: number;                // 失敗ステップ数
    skipped_steps: number;               // スキップステップ数
    execution_time_ms: number;           // 総実行時間（ミリ秒）
  };
  
  // コスト情報
  cost?: {
    compute_cost?: number;               // 計算コスト
    storage_cost?: number;               // ストレージコスト
    api_calls?: number;                  // API呼び出し回数
    total_cost?: number;                 // 合計コスト
  };
}

// 実行エラー
interface ExecutionError {
  code: string;                          // エラーコード
  message: string;                       // エラーメッセージ
  step_id?: string;                      // エラー発生ステップID
  details?: any;                         // 詳細情報
  stack_trace?: string;                  // スタックトレース
  timestamp: string;                     // エラー発生時刻
}
```

## API リクエスト/レスポンス型定義

### チェイン作成

```typescript
// チェイン作成リクエスト
interface CreateChainRequest {
  name: string;                          // チェイン名（必須）
  description?: string;                  // 説明
  category: ChainCategory;               // カテゴリー（必須）
  tags?: string[];                       // タグ
  
  steps: ChainStep[];                    // ステップ定義（必須）
  input_parameters: ChainParameter[];    // 入力パラメータ定義
  output_mapping: OutputMapping;         // 出力マッピング
  
  execution_config?: ExecutionConfig;    // 実行設定
  visibility?: ChainVisibility;          // 公開範囲
}

// チェイン作成レスポンス
interface CreateChainResponse {
  chain_id: string;                      // 作成されたチェインID
  version: number;                       // バージョン番号
  created_at: string;                    // 作成日時
}
```

### チェイン実行

```typescript
// チェイン実行リクエスト
interface ExecuteChainRequest {
  chain_id: string;                      // チェインID（必須）
  version?: number;                      // バージョン（省略時は最新）
  
  input_parameters: Record<string, any>; // 入力パラメータ値（必須）
  
  execution_config?: {
    mode?: ExecutionMode;                // 実行モード
    timeout_seconds?: number;            // タイムアウト（秒）
    async?: boolean;                     // 非同期実行
  };
  
  metadata?: Record<string, any>;        // メタデータ
}

// チェイン実行レスポンス
interface ExecuteChainResponse {
  execution_id: string;                  // 実行ID
  status: ExecutionStatus;               // 初期ステータス
  
  // 同期実行の場合
  result?: ExecutionResult;              // 実行結果
  
  // 非同期実行の場合
  polling_url?: string;                  // ポーリングURL
  estimated_time_seconds?: number;       // 推定実行時間
}
```

### 実行状態取得

```typescript
// 実行状態取得リクエスト
interface GetExecutionStatusRequest {
  execution_id: string;                  // 実行ID（必須）
  include_step_details?: boolean;        // ステップ詳細を含める
}

// 実行状態取得レスポンス
interface GetExecutionStatusResponse {
  execution: ChainExecution;             // 実行情報
  can_cancel: boolean;                   // キャンセル可能フラグ
  can_retry: boolean;                    // リトライ可能フラグ
}
```

### チェイン管理

```typescript
// チェイン一覧取得リクエスト
interface ListChainsRequest {
  category?: ChainCategory;              // カテゴリーフィルタ
  tags?: string[];                       // タグフィルタ
  status?: ChainStatus;                  // ステータスフィルタ
  visibility?: ChainVisibility;          // 公開範囲フィルタ
  
  search?: string;                       // 検索キーワード
  
  sort_by?: "name" | "created_at" | "updated_at" | "execution_count";
  sort_order?: "asc" | "desc";
  
  limit?: number;                        // 取得件数（デフォルト: 20）
  offset?: number;                       // オフセット
}

// チェイン一覧取得レスポンス
interface ListChainsResponse {
  chains: Chain[];                       // チェイン配列
  total: number;                         // 総件数
  has_more: boolean;                     // 追加データの有無
}

// チェイン更新リクエスト
interface UpdateChainRequest {
  chain_id: string;                      // チェインID（必須）
  
  name?: string;                         // チェイン名
  description?: string;                  // 説明
  category?: ChainCategory;              // カテゴリー
  tags?: string[];                       // タグ
  
  steps?: ChainStep[];                   // ステップ定義
  input_parameters?: ChainParameter[];   // 入力パラメータ
  output_mapping?: OutputMapping;        // 出力マッピング
  
  execution_config?: ExecutionConfig;    // 実行設定
  visibility?: ChainVisibility;          // 公開範囲
  status?: ChainStatus;                  // ステータス
  
  create_new_version?: boolean;          // 新バージョン作成フラグ
}

// チェイン削除リクエスト
interface DeleteChainRequest {
  chain_id: string;                      // チェインID（必須）
  version?: number;                      // バージョン（省略時は全バージョン）
}

// チェインエクスポートレスポンス
interface ExportChainResponse {
  chain_definition: any;                 // チェイン定義（JSON）
  format: "json" | "yaml";               // エクスポート形式
  version: string;                       // スキーマバージョン
}

// チェインインポートリクエスト
interface ImportChainRequest {
  chain_definition: any;                 // チェイン定義（JSON/YAML）
  format: "json" | "yaml";               // インポート形式
  
  name?: string;                         // チェイン名（上書き）
  create_as_new?: boolean;               // 新規作成フラグ
}
```

## 公開範囲型定義

```typescript
// チェイン公開範囲（タスク・ライブラリと同一仕様）
interface ChainVisibility {
  scope: VisibilityScope;                // 公開範囲
  
  // グループ公開の場合
  allowed_groups?: string[];             // 許可グループID配列
  
  // ユーザー指定の場合
  allowed_users?: string[];              // 許可ユーザーID配列
  
  // 共有設定
  sharing?: {
    allow_fork: boolean;                 // フォーク許可
    allow_export: boolean;               // エクスポート許可
    allow_execution: boolean;            // 実行許可
    require_approval?: boolean;          // 承認必須
  };
}

// 公開範囲
type VisibilityScope = 
  | "private"              // 非公開（作成者のみ）
  | "team"                 // チーム内公開
  | "organization"         // 組織内公開
  | "public"               // 完全公開
  | "custom";              // カスタム（グループ/ユーザー指定）
```

## 更新履歴

- 2025-08-07: 初版作成
  - チェイン基本型定義
  - 制御フロー型定義（条件分岐、ループ、並列実行）
  - データマッピング型定義
  - 実行管理型定義
  - API リクエスト/レスポンス型定義
  - 公開範囲型定義（タスク・ライブラリと統一）