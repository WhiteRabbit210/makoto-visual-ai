# WebクロールAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [CrawlJob](#crawljob)
   - [CrawlResult](#crawlresult)
   - [WebPage](#webpage)
   - [ExtractedData](#extracteddata)
3. [クロール設定型定義](#クロール設定型定義)
   - [CrawlConfig](#crawlconfig)
   - [CrawlRule](#crawlrule)
   - [CrawlFilter](#crawlfilter)
   - [RateLimiting](#ratelimiting)
4. [スケジュール型定義](#スケジュール型定義)
   - [CrawlSchedule](#crawlschedule)
   - [SchedulePattern](#schedulepattern)
   - [ScheduleExecution](#scheduleexecution)
5. [データ抽出型定義](#データ抽出型定義)
   - [ExtractionRule](#extractionrule)
   - [Selector](#selector)
   - [DataTransform](#datatransform)
6. [検索・要約型定義](#検索要約型定義)
   - [WebSearch](#websearch)
   - [ContentSummary](#contentsummary)
   - [KeywordExtraction](#keywordextraction)
7. [スクレイピング型定義](#スクレイピング型定義)
   - [ScrapingTemplate](#scrapingtemplate)
   - [DynamicContent](#dynamiccontent)
   - [FormInteraction](#forminteraction)
8. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [クロール実行](#クロール実行)
   - [スケジュール管理](#スケジュール管理)
   - [結果取得](#結果取得)
   - [Web検索と要約](#web検索と要約)
9. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのWebクロール機能で使用される型定義。Webページのクロール、スクレイピング、データ抽出、検索、要約などのWeb情報収集に関する構造を定義する。

## 基本型定義

### CrawlJob

クロールジョブの基本構造：

```typescript
interface CrawlJob {
  // 識別情報
  job_id: string;                         // ジョブID（UUID）
  tenant_id: string;                      // テナントID
  
  // ジョブ情報
  name: string;                           // ジョブ名
  description?: string;                   // 説明
  type: CrawlJobType;                     // ジョブタイプ
  
  // クロール対象
  targets: {
    urls?: string[];                      // 対象URL
    domains?: string[];                   // 対象ドメイン
    sitemaps?: string[];                  // サイトマップURL
    
    // 検索ベースクロール
    search_queries?: Array<{
      keywords: string[];                 // 検索キーワード
      search_engine?: SearchEngine;      // 検索エンジン
      max_results?: number;               // 最大結果数
    }>;
  };
  
  // クロール設定
  config: CrawlConfig;                    // クロール設定
  
  // データ抽出
  extraction_rules?: ExtractionRule[];    // 抽出ルール
  
  // スケジュール
  schedule?: CrawlSchedule;                // スケジュール設定
  
  // 実行状態
  status: CrawlJobStatus;                 // ジョブステータス
  current_progress?: {
    pages_crawled: number;                // クロール済みページ数
    pages_total?: number;                 // 総ページ数（推定）
    data_extracted: number;               // 抽出データ数
    errors_count: number;                 // エラー数
  };
  
  // 実行履歴
  last_execution?: {
    execution_id: string;                 // 実行ID
    started_at: string;                   // 開始時刻
    completed_at?: string;                // 完了時刻
    status: ExecutionStatus;              // 実行ステータス
  };
  
  // 統計情報
  statistics?: {
    total_executions: number;             // 総実行回数
    success_count: number;                // 成功回数
    failure_count: number;                // 失敗回数
    average_duration_seconds: number;     // 平均実行時間
    total_pages_crawled: number;         // 総クロールページ数
    total_data_extracted: number;        // 総抽出データ数
  };
  
  // メタデータ
  created_by: string;                     // 作成者
  created_at: string;                     // 作成日時
  updated_at: string;                     // 更新日時
  tags?: string[];                         // タグ
}

// クロールジョブタイプ
type CrawlJobType = 
  | "single_page"           // 単一ページ
  | "site_crawl"            // サイト全体
  | "search_based"          // 検索ベース
  | "api_crawl"             // API経由
  | "scheduled"             // スケジュール実行
  | "continuous";           // 継続的クロール

// ジョブステータス
type CrawlJobStatus = 
  | "draft"                 // 下書き
  | "ready"                 // 実行準備完了
  | "running"               // 実行中
  | "paused"                // 一時停止
  | "completed"             // 完了
  | "failed"                // 失敗
  | "cancelled";            // キャンセル

// 検索エンジン
type SearchEngine = 
  | "google"
  | "bing"
  | "duckduckgo"
  | "custom";
```

### CrawlResult

クロール結果：

```typescript
interface CrawlResult {
  // 識別情報
  result_id: string;                      // 結果ID
  job_id: string;                         // ジョブID
  execution_id: string;                   // 実行ID
  
  // クロール結果
  pages: WebPage[];                       // クロールページ
  extracted_data: ExtractedData[];        // 抽出データ
  
  // サマリー
  summary: {
    total_pages: number;                  // 総ページ数
    successful_pages: number;             // 成功ページ数
    failed_pages: number;                 // 失敗ページ数
    total_size_bytes: number;             // 総データサイズ
    
    // 時間統計
    start_time: string;                   // 開始時刻
    end_time: string;                     // 終了時刻
    duration_seconds: number;             // 実行時間
    
    // データ統計
    unique_domains: number;               // ユニークドメイン数
    unique_urls: number;                  // ユニークURL数
    data_points_extracted: number;        // 抽出データポイント数
  };
  
  // エラー情報
  errors?: Array<{
    url: string;                         // エラーURL
    error_type: string;                  // エラータイプ
    error_message: string;                // エラーメッセージ
    timestamp: string;                    // エラー発生時刻
    retry_count?: number;                 // リトライ回数
  }>;
  
  // リンク分析
  link_analysis?: {
    internal_links: number;               // 内部リンク数
    external_links: number;               // 外部リンク数
    broken_links?: string[];              // 壊れたリンク
    redirects?: Array<{                   // リダイレクト
      from: string;
      to: string;
      status_code: number;
    }>;
  };
  
  // メタデータ
  metadata?: {
    crawl_depth?: number;                 // クロール深度
    follow_redirects?: boolean;          // リダイレクト追跡
    respect_robots_txt?: boolean;        // robots.txt遵守
    user_agent?: string;                  // ユーザーエージェント
  };
}
```

### WebPage

Webページ情報：

```typescript
interface WebPage {
  // ページ情報
  url: string;                            // ページURL
  final_url?: string;                     // 最終URL（リダイレクト後）
  domain: string;                         // ドメイン
  path: string;                           // パス
  
  // メタデータ
  title?: string;                         // ページタイトル
  description?: string;                   // メタディスクリプション
  keywords?: string[];                    // メタキーワード
  author?: string;                        // 著者
  published_date?: string;                // 公開日
  modified_date?: string;                 // 更新日
  language?: string;                      // 言語
  
  // コンテンツ
  content: {
    html?: string;                        // HTML全文
    text?: string;                        // テキスト抽出
    markdown?: string;                    // Markdown変換
    
    // 構造化コンテンツ
    headings?: Array<{                    // 見出し
      level: number;                      // H1-H6
      text: string;
    }>;
    paragraphs?: string[];                // 段落
    lists?: Array<{                       // リスト
      type: "ordered" | "unordered";
      items: string[];
    }>;
    tables?: Array<{                      // テーブル
      headers?: string[];
      rows: string[][];
    }>;
  };
  
  // メディア
  media?: {
    images?: Array<{                      // 画像
      src: string;
      alt?: string;
      title?: string;
      width?: number;
      height?: number;
    }>;
    videos?: Array<{                      // 動画
      src: string;
      type?: string;
      duration?: number;
    }>;
    audios?: Array<{                      // 音声
      src: string;
      type?: string;
      duration?: number;
    }>;
  };
  
  // リンク
  links?: {
    internal: Link[];                     // 内部リンク
    external: Link[];                     // 外部リンク
    anchors: string[];                    // アンカーリンク
  };
  
  // 技術情報
  technical?: {
    status_code: number;                  // HTTPステータスコード
    content_type?: string;                // コンテンツタイプ
    content_length?: number;              // コンテンツサイズ
    encoding?: string;                    // エンコーディング
    response_time_ms?: number;            // レスポンス時間
    
    // ヘッダー情報
    headers?: Record<string, string>;     // HTTPヘッダー
    
    // JavaScript情報
    javascript?: {
      frameworks?: string[];              // 検出フレームワーク
      libraries?: string[];               // 検出ライブラリ
      requires_js?: boolean;              // JS必須フラグ
    };
  };
  
  // SEO情報
  seo?: {
    canonical_url?: string;               // カノニカルURL
    robots?: string;                      // robots設定
    sitemap?: string;                     // サイトマップURL
    
    // Open Graph
    og?: {
      title?: string;
      description?: string;
      image?: string;
      type?: string;
      url?: string;
    };
    
    // Twitter Card
    twitter?: {
      card?: string;
      title?: string;
      description?: string;
      image?: string;
    };
    
    // 構造化データ
    structured_data?: any[];              // JSON-LD等
  };
  
  // クロール情報
  crawl_info: {
    crawled_at: string;                   // クロール日時
    depth: number;                        // クロール深度
    discovery_path?: string[];            // 発見パス
  };
}

// リンク情報
interface Link {
  href: string;                           // リンク先
  text?: string;                          // リンクテキスト
  title?: string;                         // タイトル属性
  rel?: string;                           // rel属性
  target?: string;                        // target属性
}
```

### ExtractedData

抽出データ：

```typescript
interface ExtractedData {
  // 識別情報
  data_id: string;                        // データID
  source_url: string;                     // ソースURL
  extraction_rule_id?: string;            // 抽出ルールID
  
  // 抽出データ
  data: Record<string, any>;              // 抽出データ（キー・バリュー）
  
  // データ型情報
  schema?: {
    [key: string]: {
      type: "string" | "number" | "boolean" | "date" | "array" | "object";
      format?: string;                    // データフォーマット
      nullable?: boolean;                 // NULL許可
    };
  };
  
  // 検証結果
  validation?: {
    is_valid: boolean;                    // 検証成功
    errors?: Array<{                      // エラー
      field: string;
      error: string;
    }>;
    warnings?: Array<{                     // 警告
      field: string;
      warning: string;
    }>;
  };
  
  // メタデータ
  metadata?: {
    extraction_time: string;              // 抽出時刻
    selector_used?: string;               // 使用セレクタ
    confidence?: number;                  // 信頼度
    source_element?: string;              // ソース要素
  };
}
```

## クロール設定型定義

### CrawlConfig

クロール設定：

```typescript
interface CrawlConfig {
  // 基本設定
  max_pages?: number;                     // 最大ページ数
  max_depth?: number;                     // 最大深度
  timeout_seconds?: number;               // タイムアウト（秒）
  concurrent_requests?: number;           // 同時リクエスト数
  
  // クロール範囲
  scope: {
    follow_internal_links?: boolean;      // 内部リンク追跡
    follow_external_links?: boolean;      // 外部リンク追跡
    allowed_domains?: string[];           // 許可ドメイン
    blocked_domains?: string[];           // ブロックドメイン
    
    // URLパターン
    include_patterns?: string[];          // 含めるパターン（正規表現）
    exclude_patterns?: string[];          // 除外パターン（正規表現）
  };
  
  // クロールルール
  rules?: CrawlRule[];                    // クロールルール
  
  // レート制限
  rate_limiting?: RateLimiting;           // レート制限
  
  // 認証
  authentication?: {
    type: "none" | "basic" | "bearer" | "custom";
    credentials?: {
      username?: string;                  // ユーザー名
      password?: string;                  // パスワード
      token?: string;                     // トークン
      headers?: Record<string, string>;   // カスタムヘッダー
    };
    
    // セッション管理
    session?: {
      login_url?: string;                 // ログインURL
      login_form?: Record<string, string>; // ログインフォーム
      cookies?: Record<string, string>;   // クッキー
    };
  };
  
  // プロキシ設定
  proxy?: {
    enabled: boolean;
    url?: string;                         // プロキシURL
    rotation?: boolean;                   // プロキシローテーション
    auth?: {
      username: string;
      password: string;
    };
  };
  
  // ブラウザ設定（動的コンテンツ用）
  browser?: {
    enabled: boolean;                     // ブラウザ使用
    headless?: boolean;                   // ヘッドレス
    javascript?: boolean;                 // JavaScript実行
    
    // ビューポート
    viewport?: {
      width: number;
      height: number;
      device_scale_factor?: number;
    };
    
    // 待機設定
    wait?: {
      type: "load" | "domcontentloaded" | "networkidle" | "selector";
      value?: string | number;            // セレクタまたは時間
    };
    
    // スクリーンショット
    screenshot?: {
      enabled: boolean;
      full_page?: boolean;
      format?: "png" | "jpeg";
    };
  };
  
  // リトライ設定
  retry?: {
    max_attempts: number;                 // 最大試行回数
    delay_ms: number;                     // 遅延（ミリ秒）
    backoff_multiplier?: number;          // バックオフ係数
    retry_on_status?: number[];           // リトライ対象ステータス
  };
  
  // キャッシュ設定
  cache?: {
    enabled: boolean;                     // キャッシュ有効
    ttl_seconds?: number;                 // TTL（秒）
    storage?: "memory" | "disk" | "redis";
  };
}
```

### CrawlRule

クロールルール：

```typescript
interface CrawlRule {
  rule_id: string;                        // ルールID
  name: string;                           // ルール名
  
  // 適用条件
  conditions: {
    url_pattern?: string;                 // URLパターン
    domain?: string;                      // ドメイン
    path_prefix?: string;                 // パスプレフィックス
    content_type?: string;                // コンテンツタイプ
    
    // ページ属性
    has_selector?: string;                // セレクタ存在
    meta_tag?: {                         // メタタグ条件
      name: string;
      value?: string;
    };
  };
  
  // アクション
  actions: {
    extract?: boolean;                    // データ抽出
    follow_links?: boolean;               // リンク追跡
    skip?: boolean;                      // スキップ
    
    // カスタム処理
    custom_processor?: string;            // カスタム処理名
    
    // 優先度
    priority?: number;                    // 処理優先度
  };
  
  // 抽出設定
  extraction?: {
    selectors?: Selector[];               // セレクタ
    transforms?: DataTransform[];         // 変換処理
  };
}
```

### CrawlFilter

クロールフィルタ：

```typescript
interface CrawlFilter {
  // URLフィルタ
  url_filters?: {
    include?: string[];                   // 含めるURL（正規表現）
    exclude?: string[];                   // 除外URL（正規表現）
    
    // クエリパラメータ
    remove_query_params?: boolean;        // クエリパラメータ削除
    allowed_params?: string[];            // 許可パラメータ
  };
  
  // コンテンツフィルタ
  content_filters?: {
    min_content_length?: number;          // 最小コンテンツ長
    max_content_length?: number;          // 最大コンテンツ長
    
    // 言語フィルタ
    languages?: string[];                 // 許可言語
    
    // コンテンツタイプ
    allowed_types?: string[];             // 許可タイプ
    blocked_types?: string[];             // ブロックタイプ
  };
  
  // 重複除去
  deduplication?: {
    enabled: boolean;                     // 重複除去有効
    method: "url" | "content_hash" | "similarity";
    similarity_threshold?: number;        // 類似度閾値（0-1）
  };
  
  // robots.txt
  robots_txt?: {
    respect: boolean;                     // robots.txt遵守
    custom_rules?: string;                // カスタムルール
  };
}
```

### RateLimiting

レート制限：

```typescript
interface RateLimiting {
  // 基本制限
  requests_per_second?: number;           // リクエスト/秒
  requests_per_minute?: number;           // リクエスト/分
  requests_per_hour?: number;             // リクエスト/時
  
  // ドメイン別制限
  per_domain?: {
    default?: number;                     // デフォルト制限
    custom?: Record<string, number>;      // ドメイン別設定
  };
  
  // 動的調整
  adaptive?: {
    enabled: boolean;                     // 動的調整有効
    min_delay_ms: number;                 // 最小遅延
    max_delay_ms: number;                 // 最大遅延
    
    // レスポンス時間ベース
    target_response_time_ms?: number;     // 目標レスポンス時間
    
    // エラー率ベース
    max_error_rate?: number;              // 最大エラー率
  };
  
  // バースト制御
  burst?: {
    enabled: boolean;                     // バースト許可
    max_burst_size: number;               // 最大バーストサイズ
    recovery_time_seconds: number;        // 回復時間
  };
}
```

## スケジュール型定義

### CrawlSchedule

クロールスケジュール：

```typescript
interface CrawlSchedule {
  // スケジュール設定
  schedule_id: string;                    // スケジュールID
  enabled: boolean;                       // 有効/無効
  
  // スケジュールパターン
  pattern: SchedulePattern;               // スケジュールパターン
  
  // 実行時間帯
  execution_window?: {
    start_time?: string;                  // 開始時刻（HH:mm）
    end_time?: string;                    // 終了時刻（HH:mm）
    timezone?: string;                    // タイムゾーン
    
    // 営業日のみ
    business_days_only?: boolean;         // 営業日のみ
    exclude_holidays?: boolean;           // 祝日除外
  };
  
  // 実行条件
  conditions?: {
    // 前回実行からの経過時間
    min_interval_hours?: number;          // 最小間隔（時間）
    
    // データ変更検出
    check_for_changes?: boolean;          // 変更チェック
    change_detection_method?: "etag" | "last_modified" | "content_hash";
    
    // 外部トリガー
    external_trigger?: {
      webhook_url?: string;               // Webhook URL
      api_endpoint?: string;              // APIエンドポイント
    };
  };
  
  // 次回実行
  next_execution?: {
    scheduled_at: string;                 // 次回実行予定
    estimated_duration?: number;          // 推定実行時間
  };
  
  // 実行履歴
  execution_history?: ScheduleExecution[]; // 実行履歴
}

// スケジュールパターン
type SchedulePattern = 
  | CronPattern
  | IntervalPattern
  | SpecificTimePattern
  | EventDrivenPattern;

interface CronPattern {
  type: "cron";
  expression: string;                     // Cron式
  description?: string;                   // 説明
}

interface IntervalPattern {
  type: "interval";
  interval: number;                       // 間隔
  unit: "minutes" | "hours" | "days" | "weeks";
}

interface SpecificTimePattern {
  type: "specific";
  times: string[];                        // 実行時刻（HH:mm）
  days?: number[];                        // 曜日（0=日曜）
  dates?: number[];                       // 日付（1-31）
}

interface EventDrivenPattern {
  type: "event";
  event_type: string;                     // イベントタイプ
  event_source?: string;                  // イベントソース
}
```

### ScheduleExecution

スケジュール実行履歴：

```typescript
interface ScheduleExecution {
  execution_id: string;                   // 実行ID
  schedule_id: string;                    // スケジュールID
  job_id: string;                         // ジョブID
  
  // 実行時間
  scheduled_at: string;                   // 予定実行時刻
  started_at: string;                     // 開始時刻
  completed_at?: string;                  // 完了時刻
  duration_seconds?: number;              // 実行時間（秒）
  
  // 実行結果
  status: ExecutionStatus;                // 実行ステータス
  result?: {
    pages_crawled: number;                // クロールページ数
    data_extracted: number;               // 抽出データ数
    errors?: number;                      // エラー数
  };
  
  // トリガー情報
  trigger: {
    type: "scheduled" | "manual" | "api" | "webhook";
    triggered_by?: string;                // トリガー実行者
    reason?: string;                      // 実行理由
  };
  
  // エラー情報
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

// 実行ステータス
type ExecutionStatus = 
  | "pending"               // 待機中
  | "running"               // 実行中
  | "completed"             // 完了
  | "failed"                // 失敗
  | "cancelled"             // キャンセル
  | "timeout";              // タイムアウト
```

## データ抽出型定義

### ExtractionRule

データ抽出ルール：

```typescript
interface ExtractionRule {
  rule_id: string;                        // ルールID
  name: string;                           // ルール名
  description?: string;                   // 説明
  
  // 抽出対象
  target: {
    selector: Selector;                   // セレクタ
    multiple?: boolean;                   // 複数要素
    required?: boolean;                   // 必須フラグ
  };
  
  // 抽出フィールド
  fields: Array<{
    name: string;                        // フィールド名
    selector: Selector;                  // セレクタ
    
    // データ型
    type?: "text" | "number" | "date" | "url" | "image" | "html";
    
    // 抽出設定
    extract?: {
      attribute?: string;                // 属性名
      regex?: string;                   // 正規表現
      group?: number;                   // 正規表現グループ
    };
    
    // 変換処理
    transform?: DataTransform;           // データ変換
    
    // バリデーション
    validation?: {
      required?: boolean;               // 必須
      pattern?: string;                 // パターン
      min?: number;                     // 最小値
      max?: number;                     // 最大値
    };
    
    // デフォルト値
    default_value?: any;                // デフォルト値
  }>;
  
  // ページネーション
  pagination?: {
    next_page_selector?: string;        // 次ページセレクタ
    max_pages?: number;                 // 最大ページ数
    
    // 無限スクロール
    infinite_scroll?: {
      enabled: boolean;
      scroll_delay_ms?: number;         // スクロール遅延
      max_scrolls?: number;             // 最大スクロール数
    };
  };
  
  // 出力形式
  output_format?: {
    type: "json" | "csv" | "xml";
    flatten?: boolean;                  // フラット化
    delimiter?: string;                 // 区切り文字（CSV）
  };
}
```

### Selector

セレクタ定義：

```typescript
interface Selector {
  type: "css" | "xpath" | "regex" | "json_path";
  value: string;                         // セレクタ値
  
  // CSS セレクタオプション
  css_options?: {
    pseudo_element?: string;             // 疑似要素
    nth_child?: number;                  // n番目の子要素
  };
  
  // XPath オプション
  xpath_options?: {
    namespace?: Record<string, string>;  // 名前空間
  };
  
  // 正規表現オプション
  regex_options?: {
    flags?: string;                      // フラグ（gim等）
    group?: number;                      // キャプチャグループ
  };
  
  // 複合セレクタ
  chain?: Selector[];                    // チェーンセレクタ
  fallback?: Selector;                   // フォールバック
}
```

### DataTransform

データ変換：

```typescript
interface DataTransform {
  type: TransformType;                   // 変換タイプ
  
  // テキスト変換
  text?: {
    operation: "trim" | "lowercase" | "uppercase" | "capitalize" | "remove_html";
    replace?: {
      pattern: string;
      replacement: string;
    };
    split?: {
      delimiter: string;
      index?: number;
    };
  };
  
  // 数値変換
  number?: {
    operation: "parse" | "round" | "floor" | "ceil";
    precision?: number;
    multiply?: number;
    add?: number;
  };
  
  // 日付変換
  date?: {
    input_format?: string;               // 入力フォーマット
    output_format?: string;              // 出力フォーマット
    timezone?: string;                   // タイムゾーン
  };
  
  // URL変換
  url?: {
    operation: "absolute" | "relative" | "normalize";
    base_url?: string;                   // ベースURL
  };
  
  // カスタム変換
  custom?: {
    function: string;                    // 関数名
    parameters?: any[];                  // パラメータ
  };
  
  // 連鎖変換
  chain?: DataTransform[];               // 連鎖変換
}

// 変換タイプ
type TransformType = 
  | "text"
  | "number"
  | "date"
  | "url"
  | "json"
  | "custom";
```

## 検索・要約型定義

### WebSearch

Web検索：

```typescript
interface WebSearch {
  // 検索クエリ
  query: {
    keywords: string[];                  // 検索キーワード
    original_query?: string;             // 元のクエリ
    
    // 検索オプション
    options?: {
      language?: string;                 // 言語
      region?: string;                   // 地域
      safe_search?: boolean;             // セーフサーチ
      date_range?: {                    // 日付範囲
        from?: string;
        to?: string;
      };
      site?: string;                     // サイト指定
      file_type?: string;                // ファイルタイプ
    };
  };
  
  // 検索エンジン設定
  engine: {
    type: SearchEngine;                  // エンジンタイプ
    api_key?: string;                    // APIキー
    custom_search_engine_id?: string;    // カスタム検索エンジンID
  };
  
  // 検索結果
  results: Array<{
    title: string;                       // タイトル
    url: string;                         // URL
    snippet: string;                     // スニペット
    
    // 追加情報
    display_link?: string;               // 表示リンク
    mime_type?: string;                  // MIMEタイプ
    file_format?: string;                // ファイル形式
    
    // メタデータ
    metadata?: {
      published_date?: string;           // 公開日
      author?: string;                   // 著者
      site_name?: string;                // サイト名
    };
    
    // 画像検索結果
    image?: {
      thumbnail_url?: string;            // サムネイルURL
      width?: number;                    // 幅
      height?: number;                   // 高さ
    };
    
    // ランキング
    position: number;                    // 検索順位
    score?: number;                      // スコア
  }>;
  
  // 検索統計
  statistics?: {
    total_results?: number;              // 総結果数
    search_time_ms?: number;             // 検索時間
    query_correction?: string;           // クエリ修正
    related_searches?: string[];         // 関連検索
  };
}
```

### ContentSummary

コンテンツ要約：

```typescript
interface ContentSummary {
  // 要約対象
  source: {
    urls?: string[];                     // 対象URL
    content?: string[];                  // 対象コンテンツ
    type: "web_page" | "article" | "document" | "mixed";
  };
  
  // 要約結果
  summary: {
    text: string;                        // 要約テキスト
    length: number;                      // 要約長（文字数）
    
    // 構造化要約
    structured?: {
      title?: string;                    // タイトル
      main_points?: string[];            // 主要ポイント
      conclusion?: string;               // 結論
      
      // セクション別要約
      sections?: Array<{
        heading: string;
        summary: string;
      }>;
    };
    
    // 重要度スコア
    importance_scores?: Array<{
      sentence: string;
      score: number;
    }>;
  };
  
  // キーワード・エンティティ
  keywords?: KeywordExtraction;          // キーワード抽出
  
  entities?: Array<{                     // エンティティ
    text: string;
    type: "person" | "organization" | "location" | "date" | "other";
    count: number;
  }>;
  
  // 感情・トーン分析
  sentiment?: {
    overall: "positive" | "negative" | "neutral";
    score: number;                       // -1 to 1
    
    // 段落別感情
    by_paragraph?: Array<{
      text: string;
      sentiment: string;
      score: number;
    }>;
  };
  
  // 要約メタデータ
  metadata: {
    model: string;                       // 使用モデル
    compression_ratio: number;           // 圧縮率
    processing_time_ms: number;          // 処理時間
    source_language?: string;            // ソース言語
    summary_language?: string;           // 要約言語
  };
}
```

### KeywordExtraction

キーワード抽出：

```typescript
interface KeywordExtraction {
  // キーワード
  keywords: Array<{
    word: string;                        // キーワード
    score: number;                       // スコア
    frequency: number;                   // 出現頻度
    
    // 分類
    category?: string;                   // カテゴリ
    part_of_speech?: string;             // 品詞
    
    // 文脈
    context?: string[];                  // 出現文脈
    positions?: number[];                // 出現位置
  }>;
  
  // キーフレーズ
  key_phrases?: Array<{
    phrase: string;                      // フレーズ
    score: number;                       // スコア
    words: string[];                     // 構成単語
  }>;
  
  // トピック
  topics?: Array<{
    topic: string;                       // トピック
    relevance: number;                   // 関連度
    keywords: string[];                  // 関連キーワード
  }>;
  
  // 共起語
  co_occurrences?: Array<{
    word1: string;
    word2: string;
    frequency: number;
    strength: number;
  }>;
}
```

## スクレイピング型定義

### ScrapingTemplate

スクレイピングテンプレート：

```typescript
interface ScrapingTemplate {
  template_id: string;                   // テンプレートID
  name: string;                          // テンプレート名
  description?: string;                  // 説明
  
  // 対象サイト
  target_site: {
    domain: string;                      // ドメイン
    site_name?: string;                  // サイト名
    site_type?: string;                  // サイトタイプ
  };
  
  // ページタイプ定義
  page_types: Array<{
    type_name: string;                   // タイプ名
    url_pattern: string;                 // URLパターン
    
    // データ構造
    data_structure: {
      [field: string]: {
        selector: string;                // セレクタ
        type: string;                    // データ型
        required?: boolean;              // 必須
        transform?: DataTransform;       // 変換
      };
    };
    
    // ナビゲーション
    navigation?: {
      next_page?: string;                // 次ページ
      pagination?: string;               // ページネーション
      categories?: string[];             // カテゴリ
    };
  }>;
  
  // 共通設定
  common_selectors?: {
    header?: string;                     // ヘッダー
    footer?: string;                     // フッター
    navigation?: string;                 // ナビゲーション
    main_content?: string;               // メインコンテンツ
  };
  
  // バージョン管理
  version: string;                       // バージョン
  last_validated?: string;               // 最終検証日
  is_active: boolean;                   // 有効フラグ
}
```

### DynamicContent

動的コンテンツ処理：

```typescript
interface DynamicContent {
  // JavaScript実行
  javascript: {
    enabled: boolean;                    // JS実行有効
    
    // 待機戦略
    wait_strategy: {
      type: "time" | "element" | "network" | "custom";
      value?: string | number;           // 待機値
      timeout_ms?: number;               // タイムアウト
    };
    
    // インタラクション
    interactions?: Array<{
      action: "click" | "scroll" | "type" | "wait";
      selector?: string;                 // 対象セレクタ
      value?: string;                    // 入力値
      delay_ms?: number;                 // 遅延
    }>;
    
    // スクリプト実行
    scripts?: Array<{
      code: string;                      // スクリプトコード
      timing: "before" | "after";        // 実行タイミング
    }>;
  };
  
  // AJAX処理
  ajax?: {
    intercept: boolean;                  // AJAX傍受
    wait_for_requests?: string[];        // 待機リクエスト
    capture_responses?: boolean;         // レスポンス取得
  };
  
  // 無限スクロール
  infinite_scroll?: {
    enabled: boolean;
    scroll_element?: string;             // スクロール要素
    scroll_distance?: number;            // スクロール距離
    max_scrolls?: number;                // 最大スクロール数
    wait_between_scrolls_ms?: number;    // スクロール間待機
  };
  
  // 遅延読み込み
  lazy_loading?: {
    trigger_loading?: boolean;           // 読み込みトリガー
    wait_for_images?: boolean;           // 画像待機
    wait_for_videos?: boolean;           // 動画待機
  };
}
```

### FormInteraction

フォーム操作：

```typescript
interface FormInteraction {
  // フォーム識別
  form_selector: string;                 // フォームセレクタ
  form_name?: string;                    // フォーム名
  
  // フォーム入力
  inputs: Array<{
    field_selector: string;              // フィールドセレクタ
    field_name?: string;                 // フィールド名
    value: string;                       // 入力値
    
    // 入力タイプ
    input_type?: "text" | "select" | "checkbox" | "radio" | "file";
    
    // 入力オプション
    clear_first?: boolean;               // クリア後入力
    trigger_events?: string[];           // トリガーイベント
  }>;
  
  // 送信設定
  submission: {
    submit_button?: string;              // 送信ボタンセレクタ
    submit_method?: "click" | "enter" | "javascript";
    
    // 送信前処理
    before_submit?: {
      wait_ms?: number;                  // 待機時間
      execute_script?: string;           // スクリプト実行
    };
    
    // 送信後処理
    after_submit?: {
      wait_for_navigation?: boolean;     // ナビゲーション待機
      wait_for_element?: string;         // 要素待機
      capture_response?: boolean;        // レスポンス取得
    };
  };
  
  // CAPTCHA処理
  captcha?: {
    type: "recaptcha" | "hcaptcha" | "image" | "custom";
    solver?: {
      service?: string;                  // 解決サービス
      api_key?: string;                  // APIキー
    };
  };
}
```

## API リクエスト/レスポンス型定義

### クロール実行

```typescript
// クロール開始リクエスト
interface StartCrawlRequest {
  // 対象指定（必須）
  targets: {
    urls?: string[];                     // URL リスト
    search_query?: {                    // 検索クエリ
      keywords: string[];
      max_results?: number;
    };
  };
  
  // クロール設定
  config?: {
    max_pages?: number;
    max_depth?: number;
    follow_links?: boolean;
  };
  
  // 抽出ルール
  extraction_rules?: ExtractionRule[];
  
  // 実行オプション
  options?: {
    async?: boolean;                     // 非同期実行
    priority?: "low" | "normal" | "high";
    callback_url?: string;               // コールバックURL
  };
}

// クロール開始レスポンス
interface StartCrawlResponse {
  job_id: string;                        // ジョブID
  status: "queued" | "running";          // ステータス
  
  estimated_time?: number;               // 推定時間（秒）
  polling_url?: string;                  // ポーリングURL
  sse_url?: string;                      // SSE URL
}
```

### スケジュール管理

```typescript
// スケジュール作成リクエスト
interface CreateScheduleRequest {
  job_id: string;                        // ジョブID（必須）
  
  pattern: SchedulePattern;              // スケジュールパターン（必須）
  
  execution_window?: {                  // 実行時間帯
    start_time?: string;
    end_time?: string;
    timezone?: string;
  };
  
  enabled?: boolean;                     // 即座に有効化
}

// スケジュール更新リクエスト
interface UpdateScheduleRequest {
  schedule_id: string;                   // スケジュールID（必須）
  
  pattern?: SchedulePattern;             // パターン更新
  enabled?: boolean;                     // 有効/無効
  
  execution_window?: {
    start_time?: string;
    end_time?: string;
  };
}

// スケジュール一覧レスポンス
interface ListSchedulesResponse {
  schedules: CrawlSchedule[];            // スケジュールリスト
  total: number;                         // 総数
}
```

### 結果取得

```typescript
// クロール結果取得リクエスト
interface GetCrawlResultRequest {
  job_id?: string;                       // ジョブID
  execution_id?: string;                 // 実行ID
  
  // フィルタ
  filters?: {
    date_from?: string;                  // 開始日
    date_to?: string;                    // 終了日
    status?: ExecutionStatus;             // ステータス
  };
  
  // ページネーション
  pagination?: {
    limit?: number;
    offset?: number;
  };
  
  // 出力形式
  format?: "json" | "csv" | "excel";
}

// クロール結果取得レスポンス
interface GetCrawlResultResponse {
  results: CrawlResult[];                 // 結果リスト
  
  // ダウンロード
  download_urls?: {
    json?: string;                       // JSON形式
    csv?: string;                        // CSV形式
    excel?: string;                      // Excel形式
  };
  
  // 統計
  statistics?: {
    total_pages: number;
    total_data_points: number;
    total_size_bytes: number;
  };
}
```

### Web検索と要約

```typescript
// Web検索要約リクエスト
interface SearchAndSummarizeRequest {
  query: {                              // 検索クエリ（必須）
    keywords: string[];
    original_question?: string;
  };
  
  search_config?: {                     // 検索設定
    max_results?: number;
    language?: string;
    region?: string;
  };
  
  summary_config?: {                    // 要約設定
    max_length?: number;
    format?: "plain" | "structured";
    include_sources?: boolean;
  };
  
  crawl_depth?: number;                  // クロール深度
}

// Web検索要約レスポンス
interface SearchAndSummarizeResponse {
  success: boolean;
  
  // 検索結果
  search_results?: Array<{
    title: string;
    url: string;
    snippet: string;
  }>;
  
  // クロール内容
  crawled_contents?: Array<{
    url: string;
    title: string;
    content: string;
  }>;
  
  // 要約
  summary?: {
    text: string;
    key_points?: string[];
    sources?: Array<{
      url: string;
      title: string;
      relevance: number;
    }>;
  };
  
  // メタデータ
  metadata?: {
    total_sources: number;
    processing_time_ms: number;
    tokens_used?: number;
  };
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - 基本型定義（CrawlJob、CrawlResult、WebPage、ExtractedData）
  - クロール設定型定義（CrawlConfig、CrawlRule、RateLimiting）
  - スケジュール型定義（CrawlSchedule、SchedulePattern）
  - データ抽出型定義（ExtractionRule、Selector、DataTransform）
  - 検索・要約型定義（WebSearch、ContentSummary、KeywordExtraction）
  - スクレイピング型定義（ScrapingTemplate、DynamicContent、FormInteraction）
  - API リクエスト/レスポンス型定義