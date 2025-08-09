# プラグインAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [Plugin](#plugin)
   - [PluginManifest](#pluginmanifest)
   - [PluginInstance](#plugininstance)
   - [PluginExecution](#pluginexecution)
3. [プラグイン設定型定義](#プラグイン設定型定義)
   - [PluginConfig](#pluginconfig)
   - [PluginCapabilities](#plugincapabilities)
   - [PluginPermissions](#pluginpermissions)
   - [PluginDependencies](#plugindependencies)
4. [プラグインAPI型定義](#プラグインapi型定義-1)
   - [PluginAPI](#pluginapi)
   - [PluginHook](#pluginhook)
   - [PluginEvent](#pluginevent)
   - [PluginContext](#plugincontext)
5. [プラグイン実行型定義](#プラグイン実行型定義)
   - [ExecutionEnvironment](#executionenvironment)
   - [PluginSandbox](#pluginsandbox)
   - [ExecutionResult](#executionresult)
6. [プラグインUI型定義](#プラグインui型定義)
   - [UIExtension](#uiextension)
   - [UIComponent](#uicomponent)
   - [UIAction](#uiaction)
7. [プラグインストア型定義](#プラグインストア型定義)
   - [PluginPackage](#pluginpackage)
   - [PluginMarketplace](#pluginmarketplace)
   - [PluginLicense](#pluginlicense)
8. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [プラグイン登録](#プラグイン登録)
   - [プラグイン実行](#プラグイン実行)
   - [プラグイン管理](#プラグイン管理)
   - [プラグインストア](#プラグインストア)
9. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのプラグイン機能で使用される型定義。プラグインの登録、実行、管理、マーケットプレイスなど、システムの拡張機能に関する構造を定義する。

## 基本型定義

### Plugin

プラグインの基本構造：

```typescript
interface Plugin {
  // 識別情報
  plugin_id: string;                      // プラグインID（UUID）
  name: string;                           // プラグイン名
  version: string;                        // バージョン（semver形式）
  
  // メタデータ
  metadata: {
    display_name: string;                 // 表示名
    description: string;                  // 説明
    author: {                            // 作者情報
      name: string;
      email?: string;
      website?: string;
      organization?: string;
    };
    
    // カテゴリとタグ
    category: PluginCategory;             // カテゴリ
    tags: string[];                      // タグ（最大10個）
    
    // アイコンと画像
    icon?: string;                        // アイコンURL
    screenshots?: string[];               // スクリーンショット
    banner?: string;                      // バナー画像
    
    // ドキュメント
    documentation_url?: string;           // ドキュメントURL
    repository_url?: string;              // リポジトリURL
    changelog_url?: string;               // 変更履歴URL
    support_url?: string;                 // サポートURL
  };
  
  // マニフェスト
  manifest: PluginManifest;               // プラグインマニフェスト
  
  // 設定
  config: PluginConfig;                   // プラグイン設定
  
  // ステータス
  status: PluginStatus;                   // プラグインステータス
  
  // インストール情報
  installation?: {
    installed_at: string;                 // インストール日時
    installed_by: string;                 // インストール者
    installation_type: "manual" | "marketplace" | "auto";
    size_bytes?: number;                  // サイズ（バイト）
  };
  
  // 使用統計
  statistics?: {
    total_executions: number;             // 総実行回数
    total_users: number;                  // 総ユーザー数
    average_execution_time_ms?: number;   // 平均実行時間
    last_executed_at?: string;            // 最終実行日時
    rating?: number;                      // 評価（1-5）
    reviews_count?: number;               // レビュー数
  };
  
  // テナント情報
  tenant_id?: string;                     // テナントID（テナント固有プラグイン）
  is_global?: boolean;                   // グローバルプラグインフラグ
  
  // タイムスタンプ
  created_at: string;                     // 作成日時
  updated_at: string;                     // 更新日時
}

// プラグインカテゴリ
type PluginCategory = 
  | "ai_assistant"          // AIアシスタント
  | "data_processing"       // データ処理
  | "integration"           // 統合・連携
  | "visualization"         // ビジュアライゼーション
  | "automation"            // 自動化
  | "security"              // セキュリティ
  | "analytics"             // 分析
  | "communication"         // コミュニケーション
  | "productivity"          // 生産性
  | "utility"               // ユーティリティ
  | "custom";               // カスタム

// プラグインステータス
type PluginStatus = 
  | "draft"                 // 下書き
  | "pending"               // 承認待ち
  | "active"                // アクティブ
  | "inactive"              // 非アクティブ
  | "deprecated"            // 非推奨
  | "suspended"             // 停止中
  | "error";                // エラー
```

### PluginManifest

プラグインマニフェスト：

```typescript
interface PluginManifest {
  // マニフェストバージョン
  manifest_version: "1.0" | "2.0";        // マニフェストバージョン
  
  // プラグイン識別
  id: string;                             // プラグインID
  name: string;                           // プラグイン名
  version: string;                        // バージョン
  
  // エントリーポイント
  entry_points: {
    // メインエントリー
    main?: {
      file: string;                       // ファイルパス
      handler: string;                    // ハンドラー関数
      type: "javascript" | "python" | "wasm";
    };
    
    // バックグラウンド処理
    background?: {
      file: string;
      persistent?: boolean;               // 永続化
    };
    
    // UI拡張
    ui?: {
      components?: string[];              // UIコンポーネント
      pages?: string[];                   // ページ
      widgets?: string[];                 // ウィジェット
    };
    
    // APIエンドポイント
    api?: {
      endpoints?: Array<{
        path: string;
        method: string;
        handler: string;
      }>;
    };
  };
  
  // 必要機能
  capabilities: PluginCapabilities;       // 機能要件
  
  // 権限
  permissions: PluginPermissions;         // 必要権限
  
  // 依存関係
  dependencies?: PluginDependencies;      // 依存関係
  
  // ホスト要件
  host_requirements?: {
    min_version?: string;                 // 最小バージョン
    max_version?: string;                 // 最大バージョン
    features?: string[];                  // 必要機能
  };
  
  // 設定スキーマ
  config_schema?: {
    type: "object";
    properties: Record<string, any>;      // JSON Schema
    required?: string[];
  };
  
  // 国際化
  i18n?: {
    default_locale: string;               // デフォルトロケール
    supported_locales: string[];         // 対応ロケール
    translations_path?: string;          // 翻訳ファイルパス
  };
}
```

### PluginInstance

プラグインインスタンス：

```typescript
interface PluginInstance {
  // インスタンス情報
  instance_id: string;                    // インスタンスID
  plugin_id: string;                      // プラグインID
  tenant_id: string;                      // テナントID
  user_id?: string;                       // ユーザーID（ユーザー固有の場合）
  
  // 設定
  configuration: {
    settings: Record<string, any>;        // 設定値
    overrides?: Record<string, any>;      // オーバーライド設定
    
    // 環境変数
    environment?: {
      variables: Record<string, string>;  // 環境変数
      secrets?: string[];                 // シークレット参照
    };
  };
  
  // 状態
  state: {
    status: InstanceStatus;               // インスタンスステータス
    health?: InstanceHealth;              // ヘルス状態
    
    // ランタイム状態
    runtime?: {
      memory_usage_mb?: number;          // メモリ使用量
      cpu_usage_percent?: number;        // CPU使用率
      last_heartbeat?: string;           // 最終ハートビート
    };
    
    // 永続化データ
    data?: Record<string, any>;          // インスタンスデータ
  };
  
  // ライフサイクル
  lifecycle: {
    created_at: string;                   // 作成日時
    started_at?: string;                  // 開始日時
    stopped_at?: string;                  // 停止日時
    last_active_at?: string;              // 最終アクティブ日時
  };
  
  // 実行統計
  execution_stats?: {
    total_calls: number;                  // 総呼び出し回数
    successful_calls: number;             // 成功回数
    failed_calls: number;                 // 失敗回数
    average_latency_ms?: number;         // 平均レイテンシ
    total_cost?: number;                  // 総コスト
  };
}

// インスタンスステータス
type InstanceStatus = 
  | "initializing"          // 初期化中
  | "running"               // 実行中
  | "paused"                // 一時停止
  | "stopped"               // 停止
  | "error"                 // エラー
  | "terminated";           // 終了

// インスタンスヘルス
type InstanceHealth = 
  | "healthy"               // 健全
  | "degraded"              // 劣化
  | "unhealthy"             // 不健全
  | "unknown";              // 不明
```

### PluginExecution

プラグイン実行情報：

```typescript
interface PluginExecution {
  // 実行情報
  execution_id: string;                   // 実行ID
  plugin_id: string;                      // プラグインID
  instance_id: string;                    // インスタンスID
  
  // トリガー情報
  trigger: {
    type: TriggerType;                    // トリガータイプ
    source?: string;                      // トリガーソース
    event?: string;                       // イベント名
    user_id?: string;                     // 実行ユーザー
  };
  
  // 入力データ
  input: {
    parameters?: Record<string, any>;     // パラメータ
    payload?: any;                        // ペイロード
    context?: PluginContext;              // 実行コンテキスト
  };
  
  // 実行結果
  result?: {
    status: ExecutionStatus;              // 実行ステータス
    output?: any;                         // 出力データ
    logs?: string[];                      // ログ
    metrics?: Record<string, number>;     // メトリクス
    
    // エラー情報
    error?: {
      code: string;
      message: string;
      stack?: string;
      details?: any;
    };
  };
  
  // タイミング
  timing: {
    queued_at?: string;                   // キュー投入時刻
    started_at: string;                   // 開始時刻
    completed_at?: string;                // 完了時刻
    duration_ms?: number;                 // 実行時間（ミリ秒）
  };
  
  // リソース使用
  resources?: {
    cpu_time_ms?: number;                 // CPU時間
    memory_peak_mb?: number;              // メモリピーク
    network_bytes?: number;               // ネットワーク通信量
    storage_bytes?: number;               // ストレージ使用量
  };
  
  // コスト
  cost?: {
    compute_cost?: number;                // 計算コスト
    storage_cost?: number;                // ストレージコスト
    network_cost?: number;                // ネットワークコスト
    total_cost?: number;                  // 総コスト
    currency?: string;                    // 通貨
  };
}

// トリガータイプ
type TriggerType = 
  | "manual"                // 手動実行
  | "api"                   // API呼び出し
  | "event"                 // イベント駆動
  | "schedule"              // スケジュール
  | "webhook"               // Webhook
  | "system";               // システム

// 実行ステータス
type ExecutionStatus = 
  | "pending"               // 待機中
  | "running"               // 実行中
  | "completed"             // 完了
  | "failed"                // 失敗
  | "cancelled"             // キャンセル
  | "timeout";              // タイムアウト
```

## プラグイン設定型定義

### PluginConfig

プラグイン設定：

```typescript
interface PluginConfig {
  // 基本設定
  enabled: boolean;                        // 有効/無効
  auto_start?: boolean;                   // 自動起動
  priority?: number;                      // 優先度（0-100）
  
  // 実行設定
  execution: {
    timeout_seconds?: number;              // タイムアウト（秒）
    max_retries?: number;                  // 最大リトライ回数
    retry_delay_ms?: number;               // リトライ遅延
    
    // 同時実行制御
    concurrency?: {
      max_instances?: number;              // 最大インスタンス数
      max_executions?: number;             // 最大同時実行数
      queue_size?: number;                 // キューサイズ
    };
    
    // スケジュール実行
    schedule?: {
      enabled: boolean;
      cron_expression?: string;            // Cron式
      timezone?: string;                   // タイムゾーン
    };
  };
  
  // リソース制限
  resources?: {
    max_memory_mb?: number;                // 最大メモリ（MB）
    max_cpu_percent?: number;              // 最大CPU使用率（%）
    max_storage_mb?: number;               // 最大ストレージ（MB）
    max_network_bandwidth_mbps?: number;   // 最大ネットワーク帯域
  };
  
  // セキュリティ設定
  security?: {
    sandbox_enabled?: boolean;             // サンドボックス有効
    network_access?: "none" | "restricted" | "full";
    allowed_domains?: string[];            // 許可ドメイン
    blocked_domains?: string[];            // ブロックドメイン
  };
  
  // ログ設定
  logging?: {
    level: "debug" | "info" | "warning" | "error";
    retention_days?: number;               // ログ保持期間
    forward_to?: string;                  // ログ転送先
  };
  
  // カスタム設定
  custom_settings?: Record<string, any>;   // プラグイン固有設定
}
```

### PluginCapabilities

プラグイン機能要件：

```typescript
interface PluginCapabilities {
  // コア機能
  core: {
    chat?: boolean;                        // チャット機能
    image_generation?: boolean;            // 画像生成
    audio_processing?: boolean;            // 音声処理
    task_management?: boolean;             // タスク管理
    data_analysis?: boolean;               // データ分析
  };
  
  // API アクセス
  api_access?: {
    internal_api?: boolean;                // 内部API
    external_api?: boolean;                // 外部API
    webhooks?: boolean;                    // Webhook
    websocket?: boolean;                   // WebSocket
    sse?: boolean;                        // Server-Sent Events
  };
  
  // データアクセス
  data_access?: {
    read_user_data?: boolean;              // ユーザーデータ読み取り
    write_user_data?: boolean;             // ユーザーデータ書き込み
    read_system_data?: boolean;            // システムデータ読み取り
    database_access?: boolean;             // データベースアクセス
    file_system?: boolean;                 // ファイルシステム
  };
  
  // UI 拡張
  ui_extension?: {
    custom_components?: boolean;           // カスタムコンポーネント
    custom_pages?: boolean;                // カスタムページ
    menu_items?: boolean;                  // メニュー項目
    toolbar_buttons?: boolean;             // ツールバーボタン
    sidebars?: boolean;                   // サイドバー
  };
  
  // 処理能力
  processing?: {
    background_jobs?: boolean;             // バックグラウンドジョブ
    scheduled_tasks?: boolean;             // スケジュールタスク
    real_time?: boolean;                  // リアルタイム処理
    batch_processing?: boolean;            // バッチ処理
    streaming?: boolean;                   // ストリーミング
  };
  
  // 統合
  integrations?: {
    external_services?: string[];         // 外部サービス
    oauth_providers?: string[];           // OAuth プロバイダー
    payment_gateways?: string[];          // 決済ゲートウェイ
  };
}
```

### PluginPermissions

プラグイン権限：

```typescript
interface PluginPermissions {
  // スコープ
  scopes: PermissionScope[];              // 権限スコープ
  
  // リソースアクセス
  resources?: {
    // ユーザーリソース
    user?: {
      read_profile?: boolean;              // プロフィール読み取り
      update_profile?: boolean;            // プロフィール更新
      read_preferences?: boolean;          // 設定読み取り
      update_preferences?: boolean;        // 設定更新
    };
    
    // チャットリソース
    chat?: {
      read_messages?: boolean;             // メッセージ読み取り
      send_messages?: boolean;             // メッセージ送信
      delete_messages?: boolean;           // メッセージ削除
      read_history?: boolean;              // 履歴読み取り
    };
    
    // ファイルリソース
    files?: {
      read?: boolean;                      // ファイル読み取り
      write?: boolean;                     // ファイル書き込み
      delete?: boolean;                    // ファイル削除
      upload?: boolean;                    // アップロード
      download?: boolean;                  // ダウンロード
    };
    
    // システムリソース
    system?: {
      read_config?: boolean;               // 設定読み取り
      modify_config?: boolean;             // 設定変更
      access_logs?: boolean;               // ログアクセス
      manage_plugins?: boolean;            // プラグイン管理
    };
  };
  
  // ネットワークアクセス
  network?: {
    outbound?: {
      enabled: boolean;
      allowed_protocols?: string[];       // 許可プロトコル
      allowed_ports?: number[];           // 許可ポート
      allowed_hosts?: string[];           // 許可ホスト
    };
    
    inbound?: {
      enabled: boolean;
      listen_ports?: number[];            // リッスンポート
    };
  };
  
  // 特権操作
  privileged?: {
    system_calls?: boolean;               // システムコール
    native_code?: boolean;                // ネイティブコード実行
    shell_access?: boolean;               // シェルアクセス
  };
}

// 権限スコープ
type PermissionScope = 
  | "read:user"             // ユーザー情報読み取り
  | "write:user"            // ユーザー情報書き込み
  | "read:chat"             // チャット読み取り
  | "write:chat"            // チャット書き込み
  | "read:files"            // ファイル読み取り
  | "write:files"           // ファイル書き込み
  | "execute:tasks"         // タスク実行
  | "manage:plugins"        // プラグイン管理
  | "access:api"            // API アクセス
  | "admin:system";         // システム管理
```

### PluginDependencies

プラグイン依存関係：

```typescript
interface PluginDependencies {
  // プラグイン依存
  plugins?: Array<{
    plugin_id: string;                     // プラグインID
    version?: string;                      // バージョン要件
    optional?: boolean;                    // オプショナル
  }>;
  
  // ライブラリ依存
  libraries?: {
    // JavaScript/TypeScript
    npm?: Record<string, string>;          // NPMパッケージ
    
    // Python
    pip?: Record<string, string>;          // Pipパッケージ
    
    // システムライブラリ
    system?: string[];                     // システムライブラリ
  };
  
  // サービス依存
  services?: Array<{
    name: string;                          // サービス名
    version?: string;                      // バージョン
    endpoint?: string;                     // エンドポイント
    required: boolean;                     // 必須フラグ
  }>;
  
  // リソース要件
  resources?: {
    min_memory_mb?: number;                // 最小メモリ
    min_storage_mb?: number;               // 最小ストレージ
    gpu_required?: boolean;                // GPU必須
  };
}
```

## プラグインAPI型定義

### PluginAPI

プラグインAPI：

```typescript
interface PluginAPI {
  // コアAPI
  core: {
    // メッセージング
    sendMessage: (message: any) => Promise<void>;
    onMessage: (handler: (message: any) => void) => void;
    
    // ストレージ
    storage: {
      get: (key: string) => Promise<any>;
      set: (key: string, value: any) => Promise<void>;
      delete: (key: string) => Promise<void>;
      list: (prefix?: string) => Promise<string[]>;
    };
    
    // ログ
    logger: {
      debug: (message: string, ...args: any[]) => void;
      info: (message: string, ...args: any[]) => void;
      warn: (message: string, ...args: any[]) => void;
      error: (message: string, ...args: any[]) => void;
    };
  };
  
  // チャットAPI
  chat?: {
    sendMessage: (content: string, options?: any) => Promise<void>;
    getHistory: (limit?: number) => Promise<any[]>;
    onNewMessage: (handler: (message: any) => void) => void;
  };
  
  // UI API
  ui?: {
    showNotification: (message: string, type?: string) => void;
    openModal: (content: any) => Promise<any>;
    registerComponent: (component: UIComponent) => void;
    updateComponent: (id: string, data: any) => void;
  };
  
  // データAPI
  data?: {
    query: (query: string, params?: any) => Promise<any[]>;
    insert: (table: string, data: any) => Promise<string>;
    update: (table: string, id: string, data: any) => Promise<void>;
    delete: (table: string, id: string) => Promise<void>;
  };
  
  // HTTP API
  http?: {
    get: (url: string, options?: any) => Promise<any>;
    post: (url: string, data?: any, options?: any) => Promise<any>;
    put: (url: string, data?: any, options?: any) => Promise<any>;
    delete: (url: string, options?: any) => Promise<any>;
  };
  
  // イベントAPI
  events?: {
    emit: (event: string, data?: any) => void;
    on: (event: string, handler: (data: any) => void) => void;
    off: (event: string, handler?: (data: any) => void) => void;
  };
}
```

### PluginHook

プラグインフック：

```typescript
interface PluginHook {
  // フック情報
  hook_id: string;                        // フックID
  name: string;                           // フック名
  type: HookType;                        // フックタイプ
  
  // タイミング
  timing: {
    phase: "before" | "after" | "around"; // 実行フェーズ
    priority?: number;                    // 優先度（0-100）
  };
  
  // ハンドラー
  handler: {
    function: string;                     // 関数名
    async?: boolean;                      // 非同期フラグ
  };
  
  // フィルタ
  filter?: {
    events?: string[];                    // 対象イベント
    conditions?: Record<string, any>;     // 条件
  };
  
  // 変換
  transform?: {
    input?: (data: any) => any;          // 入力変換
    output?: (data: any) => any;         // 出力変換
  };
}

// フックタイプ
type HookType = 
  | "lifecycle"             // ライフサイクル
  | "data"                  // データ
  | "ui"                    // UI
  | "api"                   // API
  | "event"                 // イベント
  | "custom";               // カスタム
```

### PluginEvent

プラグインイベント：

```typescript
interface PluginEvent {
  // イベント情報
  event_id: string;                       // イベントID
  event_type: string;                     // イベントタイプ
  event_name: string;                     // イベント名
  
  // ソース
  source: {
    plugin_id?: string;                   // プラグインID
    instance_id?: string;                 // インスタンスID
    user_id?: string;                     // ユーザーID
  };
  
  // データ
  data: any;                              // イベントデータ
  
  // メタデータ
  metadata?: {
    timestamp: string;                    // タイムスタンプ
    correlation_id?: string;              // 相関ID
    sequence?: number;                    // シーケンス番号
  };
  
  // 伝播制御
  propagation?: {
    bubbles?: boolean;                    // バブリング
    cancelable?: boolean;                 // キャンセル可能
    stopped?: boolean;                    // 伝播停止
  };
}
```

### PluginContext

プラグインコンテキスト：

```typescript
interface PluginContext {
  // 実行コンテキスト
  execution: {
    execution_id: string;                 // 実行ID
    plugin_id: string;                    // プラグインID
    instance_id: string;                  // インスタンスID
    tenant_id: string;                    // テナントID
  };
  
  // ユーザーコンテキスト
  user?: {
    user_id: string;                      // ユーザーID
    username?: string;                    // ユーザー名
    email?: string;                       // メールアドレス
    roles?: string[];                     // ロール
  };
  
  // セッションコンテキスト
  session?: {
    session_id: string;                   // セッションID
    started_at: string;                   // 開始時刻
    locale?: string;                      // ロケール
    timezone?: string;                    // タイムゾーン
  };
  
  // リクエストコンテキスト
  request?: {
    method?: string;                      // HTTPメソッド
    path?: string;                        // パス
    headers?: Record<string, string>;     // ヘッダー
    query?: Record<string, string>;       // クエリパラメータ
  };
  
  // 環境コンテキスト
  environment: {
    mode: "development" | "staging" | "production";
    version: string;                      // システムバージョン
    features?: string[];                  // 有効機能
  };
}
```

## プラグイン実行型定義

### ExecutionEnvironment

実行環境：

```typescript
interface ExecutionEnvironment {
  // ランタイム
  runtime: {
    type: RuntimeType;                    // ランタイムタイプ
    version: string;                      // バージョン
    
    // Node.js
    nodejs?: {
      version: string;
      modules?: string[];                 // 利用可能モジュール
    };
    
    // Python
    python?: {
      version: string;
      packages?: string[];                // 利用可能パッケージ
    };
    
    // WebAssembly
    wasm?: {
      features?: string[];                // 有効機能
      memory_pages?: number;              // メモリページ数
    };
  };
  
  // サンドボックス
  sandbox?: PluginSandbox;                // サンドボックス設定
  
  // リソース
  resources: {
    memory_limit_mb: number;              // メモリ制限
    cpu_limit?: number;                   // CPU制限
    timeout_seconds: number;              // タイムアウト
    
    // ファイルシステム
    filesystem?: {
      enabled: boolean;
      temp_dir?: string;                  // 一時ディレクトリ
      max_size_mb?: number;               // 最大サイズ
    };
  };
  
  // ネットワーク
  network?: {
    enabled: boolean;
    proxy?: string;                       // プロキシ設定
    dns_servers?: string[];               // DNSサーバー
  };
}

// ランタイムタイプ
type RuntimeType = 
  | "nodejs"
  | "python"
  | "wasm"
  | "docker"
  | "lambda";
```

### PluginSandbox

サンドボックス設定：

```typescript
interface PluginSandbox {
  // 分離レベル
  isolation_level: IsolationLevel;        // 分離レベル
  
  // セキュリティ
  security: {
    // システムコール制限
    syscall_filter?: {
      allowed?: string[];                 // 許可システムコール
      blocked?: string[];                 // ブロックシステムコール
    };
    
    // ファイルアクセス制限
    filesystem?: {
      read_only?: boolean;                // 読み取り専用
      allowed_paths?: string[];           // 許可パス
      blocked_paths?: string[];           // ブロックパス
    };
    
    // プロセス制限
    process?: {
      max_processes?: number;             // 最大プロセス数
      max_threads?: number;               // 最大スレッド数
    };
  };
  
  // コンテナ設定（Docker使用時）
  container?: {
    image: string;                        // コンテナイメージ
    command?: string[];                   // 実行コマンド
    env?: Record<string, string>;         // 環境変数
    volumes?: Array<{                     // ボリュームマウント
      host: string;
      container: string;
      readonly?: boolean;
    }>;
  };
  
  // WASM設定
  wasm?: {
    imports?: Record<string, any>;        // インポート関数
    memory?: {
      initial: number;                    // 初期メモリ
      maximum?: number;                   // 最大メモリ
    };
  };
}

// 分離レベル
type IsolationLevel = 
  | "none"                  // 分離なし
  | "process"               // プロセス分離
  | "container"             // コンテナ分離
  | "vm";                   // VM分離
```

### ExecutionResult

実行結果：

```typescript
interface ExecutionResult {
  // 結果情報
  execution_id: string;                   // 実行ID
  status: ExecutionStatus;                // 実行ステータス
  
  // 出力
  output?: {
    data?: any;                           // 出力データ
    type?: string;                        // データ型
    encoding?: string;                    // エンコーディング
  };
  
  // 副作用
  side_effects?: {
    // ファイル変更
    files_created?: string[];             // 作成ファイル
    files_modified?: string[];            // 変更ファイル
    files_deleted?: string[];             // 削除ファイル
    
    // データ変更
    data_written?: Array<{
      type: string;
      id: string;
      operation: string;
    }>;
    
    // 外部呼び出し
    api_calls?: Array<{
      url: string;
      method: string;
      status_code?: number;
    }>;
  };
  
  // ログ
  logs?: {
    stdout?: string;                      // 標準出力
    stderr?: string;                      // 標準エラー
    system?: LogEntry[];                  // システムログ
  };
  
  // メトリクス
  metrics?: {
    execution_time_ms: number;            // 実行時間
    memory_used_mb: number;               // メモリ使用量
    cpu_time_ms?: number;                 // CPU時間
    io_operations?: number;               // I/O操作数
  };
  
  // エラー
  error?: {
    type: string;                         // エラータイプ
    message: string;                      // エラーメッセージ
    code?: string;                        // エラーコード
    stack?: string;                       // スタックトレース
    context?: any;                        // エラーコンテキスト
  };
}

// ログエントリ
interface LogEntry {
  timestamp: string;
  level: "debug" | "info" | "warning" | "error";
  message: string;
  context?: any;
}
```

## プラグインUI型定義

### UIExtension

UI拡張：

```typescript
interface UIExtension {
  // 拡張ポイント
  extension_points: Array<{
    location: ExtensionLocation;          // 拡張場所
    component: UIComponent;               // コンポーネント
    order?: number;                      // 表示順序
  }>;
  
  // メニュー拡張
  menu_items?: Array<{
    id: string;                          // メニューID
    label: string;                        // ラベル
    icon?: string;                        // アイコン
    parent?: string;                      // 親メニュー
    action: UIAction;                     // アクション
    visible?: boolean;                    // 表示フラグ
    enabled?: boolean;                    // 有効フラグ
  }>;
  
  // ツールバー拡張
  toolbar_items?: Array<{
    id: string;
    icon: string;
    tooltip?: string;
    action: UIAction;
    position?: "left" | "center" | "right";
  }>;
  
  // パネル拡張
  panels?: Array<{
    id: string;
    title: string;
    position: "left" | "right" | "bottom";
    component: UIComponent;
    resizable?: boolean;
    collapsible?: boolean;
  }>;
  
  // モーダル定義
  modals?: Array<{
    id: string;
    title: string;
    component: UIComponent;
    size?: "small" | "medium" | "large" | "fullscreen";
    closable?: boolean;
  }>;
}

// 拡張場所
type ExtensionLocation = 
  | "header"
  | "sidebar"
  | "main_content"
  | "footer"
  | "toolbar"
  | "context_menu"
  | "settings"
  | "dashboard";
```

### UIComponent

UIコンポーネント：

```typescript
interface UIComponent {
  // コンポーネント情報
  id: string;                            // コンポーネントID
  type: ComponentType;                   // コンポーネントタイプ
  
  // レンダリング
  render: {
    // HTML/React/Vue
    html?: string;                        // HTMLテンプレート
    react?: any;                          // Reactコンポーネント
    vue?: any;                            // Vueコンポーネント
    
    // カスタムレンダラー
    custom?: {
      renderer: string;                   // レンダラー関数
      props?: any;                        // プロパティ
    };
  };
  
  // スタイル
  styles?: {
    css?: string;                         // CSSスタイル
    theme?: Record<string, any>;          // テーマ設定
  };
  
  // インタラクション
  interactions?: {
    events?: Record<string, string>;      // イベントハンドラー
    bindings?: Record<string, any>;       // データバインディング
  };
  
  // ライフサイクル
  lifecycle?: {
    onMount?: string;                     // マウント時
    onUpdate?: string;                    // 更新時
    onUnmount?: string;                   // アンマウント時
  };
}

// コンポーネントタイプ
type ComponentType = 
  | "widget"
  | "panel"
  | "modal"
  | "form"
  | "chart"
  | "table"
  | "custom";
```

### UIAction

UIアクション：

```typescript
interface UIAction {
  type: ActionType;                       // アクションタイプ
  
  // コマンド実行
  command?: {
    name: string;                         // コマンド名
    parameters?: any;                     // パラメータ
  };
  
  // 関数呼び出し
  function?: {
    name: string;                         // 関数名
    arguments?: any[];                    // 引数
  };
  
  // ナビゲーション
  navigation?: {
    url?: string;                         // URL
    target?: "_self" | "_blank" | "_parent" | "_top";
    params?: Record<string, string>;      // パラメータ
  };
  
  // イベント発火
  event?: {
    name: string;                         // イベント名
    data?: any;                           // イベントデータ
  };
}

// アクションタイプ
type ActionType = 
  | "command"
  | "function"
  | "navigation"
  | "event"
  | "modal"
  | "notification";
```

## プラグインストア型定義

### PluginPackage

プラグインパッケージ：

```typescript
interface PluginPackage {
  // パッケージ情報
  package_id: string;                     // パッケージID
  plugin_id: string;                      // プラグインID
  version: string;                        // バージョン
  
  // ファイル
  files: {
    manifest: string;                     // マニフェストファイル
    main?: string;                        // メインファイル
    assets?: string[];                    // アセットファイル
    documentation?: string;               // ドキュメント
  };
  
  // パッケージメタデータ
  metadata: {
    size_bytes: number;                   // サイズ
    checksum: string;                     // チェックサム
    signature?: string;                   // 署名
    
    // ビルド情報
    build?: {
      timestamp: string;                  // ビルド日時
      environment?: string;               // ビルド環境
      commit?: string;                    // コミットハッシュ
    };
  };
  
  // 配布情報
  distribution: {
    download_url: string;                 // ダウンロードURL
    update_url?: string;                  // 更新確認URL
    mirror_urls?: string[];               // ミラーURL
  };
  
  // 互換性
  compatibility: {
    min_system_version: string;           // 最小システムバージョン
    max_system_version?: string;          // 最大システムバージョン
    platforms?: string[];                 // 対応プラットフォーム
    architectures?: string[];             // 対応アーキテクチャ
  };
}
```

### PluginMarketplace

プラグインマーケットプレイス：

```typescript
interface PluginMarketplace {
  // マーケット情報
  listing_id: string;                     // リスティングID
  plugin_id: string;                      // プラグインID
  
  // 公開情報
  visibility: "public" | "private" | "unlisted";
  featured?: boolean;                     // 注目プラグイン
  verified?: boolean;                     // 検証済み
  
  // 価格設定
  pricing: {
    model: PricingModel;                  // 価格モデル
    price?: number;                       // 価格
    currency?: string;                    // 通貨
    
    // サブスクリプション
    subscription?: {
      period: "monthly" | "yearly";       // 期間
      price: number;                      // 価格
      trial_days?: number;                // 試用期間
    };
    
    // 使用量ベース
    usage_based?: {
      metric: string;                     // メトリクス
      price_per_unit: number;             // 単価
      included_units?: number;            // 含まれる単位
    };
  };
  
  // 評価とレビュー
  ratings: {
    average: number;                      // 平均評価（1-5）
    count: number;                        // 評価数
    distribution: {                       // 評価分布
      "1": number;
      "2": number;
      "3": number;
      "4": number;
      "5": number;
    };
  };
  
  reviews?: Array<{
    review_id: string;
    user_id: string;
    rating: number;
    title?: string;
    comment?: string;
    created_at: string;
    helpful_count?: number;
  }>;
  
  // 統計
  statistics: {
    downloads: number;                    // ダウンロード数
    active_installs: number;              // アクティブインストール数
    revenue?: number;                     // 収益
  };
  
  // サポート
  support: {
    email?: string;                       // サポートメール
    url?: string;                         // サポートURL
    response_time?: string;               // 応答時間
    languages?: string[];                 // 対応言語
  };
}

// 価格モデル
type PricingModel = 
  | "free"
  | "one_time"
  | "subscription"
  | "usage_based"
  | "freemium";
```

### PluginLicense

プラグインライセンス：

```typescript
interface PluginLicense {
  // ライセンス情報
  license_id: string;                     // ライセンスID
  plugin_id: string;                      // プラグインID
  type: LicenseType;                      // ライセンスタイプ
  
  // ライセンシー
  licensee: {
    user_id?: string;                     // ユーザーID
    tenant_id?: string;                   // テナントID
    organization?: string;                // 組織名
    email?: string;                       // メールアドレス
  };
  
  // 有効期間
  validity: {
    issued_at: string;                    // 発行日
    expires_at?: string;                  // 有効期限
    activated_at?: string;                // アクティベート日
    is_active: boolean;                   // 有効フラグ
  };
  
  // 制限
  restrictions?: {
    max_users?: number;                   // 最大ユーザー数
    max_instances?: number;               // 最大インスタンス数
    allowed_features?: string[];          // 許可機能
    blocked_features?: string[];          // ブロック機能
  };
  
  // ライセンスキー
  key: {
    value: string;                        // キー値
    format: "uuid" | "serial" | "custom"; // キー形式
    encrypted?: boolean;                  // 暗号化フラグ
  };
  
  // 検証
  verification?: {
    method: "online" | "offline" | "both"; // 検証方法
    server_url?: string;                  // 検証サーバー
    public_key?: string;                  // 公開鍵
  };
}

// ライセンスタイプ
type LicenseType = 
  | "mit"
  | "apache2"
  | "gpl"
  | "proprietary"
  | "trial"
  | "commercial";
```

## API リクエスト/レスポンス型定義

### プラグイン登録

```typescript
// プラグイン登録リクエスト
interface RegisterPluginRequest {
  // パッケージ（必須）
  package: {
    file?: string;                        // Base64エンコード
    url?: string;                         // パッケージURL
  };
  
  // メタデータ
  metadata?: {
    name?: string;
    description?: string;
    category?: PluginCategory;
    tags?: string[];
  };
  
  // 設定
  config?: Partial<PluginConfig>;
  
  // インストールオプション
  options?: {
    auto_enable?: boolean;                // 自動有効化
    auto_start?: boolean;                 // 自動起動
    validate?: boolean;                   // 検証実行
  };
}

// プラグイン登録レスポンス
interface RegisterPluginResponse {
  plugin: Plugin;                         // プラグイン情報
  
  installation: {
    status: "success" | "pending" | "failed";
    message?: string;
    warnings?: string[];
  };
  
  validation?: {
    passed: boolean;
    errors?: string[];
    warnings?: string[];
  };
}
```

### プラグイン実行

```typescript
// プラグイン実行リクエスト
interface ExecutePluginRequest {
  plugin_id: string;                      // プラグインID（必須）
  
  // 実行パラメータ
  input?: {
    action?: string;                      // アクション名
    parameters?: Record<string, any>;     // パラメータ
    data?: any;                           // データ
  };
  
  // 実行オプション
  options?: {
    async?: boolean;                      // 非同期実行
    timeout_seconds?: number;             // タイムアウト
    priority?: "low" | "normal" | "high"; // 優先度
  };
  
  // コンテキスト
  context?: Partial<PluginContext>;
}

// プラグイン実行レスポンス
interface ExecutePluginResponse {
  execution_id: string;                   // 実行ID
  
  // 同期実行の場合
  result?: ExecutionResult;               // 実行結果
  
  // 非同期実行の場合
  status?: "queued" | "running";
  polling_url?: string;                   // ポーリングURL
  estimated_time?: number;                // 推定時間
}
```

### プラグイン管理

```typescript
// プラグイン一覧取得リクエスト
interface ListPluginsRequest {
  // フィルタ
  filters?: {
    category?: PluginCategory;
    status?: PluginStatus;
    tags?: string[];
    installed?: boolean;
  };
  
  // 検索
  search?: string;
  
  // ページネーション
  pagination?: {
    limit?: number;
    offset?: number;
  };
  
  // ソート
  sort?: {
    field: "name" | "created_at" | "downloads" | "rating";
    order: "asc" | "desc";
  };
}

// プラグイン更新リクエスト
interface UpdatePluginRequest {
  plugin_id: string;                      // プラグインID（必須）
  
  // 更新内容
  updates: {
    config?: Partial<PluginConfig>;
    metadata?: Partial<Plugin["metadata"]>;
    status?: PluginStatus;
  };
  
  // バージョン更新
  version?: {
    target_version?: string;              // 対象バージョン
    auto_update?: boolean;                // 自動更新
  };
}

// プラグイン削除リクエスト
interface DeletePluginRequest {
  plugin_id: string;                      // プラグインID（必須）
  
  options?: {
    remove_data?: boolean;                // データ削除
    remove_config?: boolean;              // 設定削除
    force?: boolean;                      // 強制削除
  };
}
```

### プラグインストア

```typescript
// マーケットプレイス検索リクエスト
interface SearchMarketplaceRequest {
  query?: string;                         // 検索クエリ
  
  filters?: {
    category?: PluginCategory;
    pricing?: PricingModel;
    min_rating?: number;
    verified_only?: boolean;
  };
  
  sort?: {
    by: "relevance" | "downloads" | "rating" | "newest" | "price";
    order?: "asc" | "desc";
  };
  
  pagination?: {
    page?: number;
    per_page?: number;
  };
}

// プラグイン購入リクエスト
interface PurchasePluginRequest {
  listing_id: string;                     // リスティングID（必須）
  
  payment?: {
    method: "credit_card" | "paypal" | "invoice";
    token?: string;                       // 決済トークン
  };
  
  license?: {
    type?: LicenseType;
    users?: number;                       // ユーザー数
    period?: string;                      // 期間
  };
}

// プラグイン購入レスポンス
interface PurchasePluginResponse {
  transaction_id: string;                 // トランザクションID
  license: PluginLicense;                 // ライセンス情報
  
  download: {
    url: string;                          // ダウンロードURL
    expires_at: string;                   // 有効期限
  };
  
  receipt?: {
    number: string;                       // 領収書番号
    amount: number;                       // 金額
    currency: string;                     // 通貨
    pdf_url?: string;                     // PDF URL
  };
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - 基本型定義（Plugin、PluginManifest、PluginInstance、PluginExecution）
  - プラグイン設定型定義（PluginConfig、PluginCapabilities、PluginPermissions）
  - プラグインAPI型定義（PluginAPI、PluginHook、PluginEvent、PluginContext）
  - プラグイン実行型定義（ExecutionEnvironment、PluginSandbox、ExecutionResult）
  - プラグインUI型定義（UIExtension、UIComponent、UIAction）
  - プラグインストア型定義（PluginPackage、PluginMarketplace、PluginLicense）
  - API リクエスト/レスポンス型定義