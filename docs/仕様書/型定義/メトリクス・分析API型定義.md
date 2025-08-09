# メトリクス・分析API型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [Metric](#metric)
   - [MetricEvent](#metricevent)
   - [DataPoint](#datapoint)
   - [TimeSeries](#timeseries)
3. [使用状況メトリクス型定義](#使用状況メトリクス型定義)
   - [UsageMetrics](#usagemetrics)
   - [APIUsage](#apiusage)
   - [UserActivity](#useractivity)
   - [ResourceConsumption](#resourceconsumption)
4. [パフォーマンスメトリクス型定義](#パフォーマンスメトリクス型定義)
   - [PerformanceMetrics](#performancemetrics)
   - [ResponseTime](#responsetime)
   - [Throughput](#throughput)
   - [Latency](#latency)
5. [システムヘルスメトリクス型定義](#システムヘルスメトリクス型定義)
   - [SystemHealth](#systemhealth)
   - [ResourceMetrics](#resourcemetrics)
   - [ServiceHealth](#servicehealth)
6. [ビジネス分析型定義](#ビジネス分析型定義)
   - [BusinessAnalytics](#businessanalytics)
   - [UserEngagement](#userengagement)
   - [ConversionMetrics](#conversionmetrics)
   - [RetentionMetrics](#retentionmetrics)
7. [データウェアハウス連携型定義](#データウェアハウス連携型定義)
   - [AthenaQuery](#athenaquery)
   - [SynapseQuery](#synapsequery)
   - [BigQueryIntegration](#bigqueryintegration)
   - [ParquetSchema](#parquetschema)
8. [リアルタイム監視型定義](#リアルタイム監視型定義)
   - [RealtimeMonitoring](#realtimemonitoring)
   - [AlertConfiguration](#alertconfiguration)
   - [StreamingMetrics](#streamingmetrics)
9. [ダッシュボード・レポート型定義](#ダッシュボードレポート型定義)
   - [Dashboard](#dashboard)
   - [Report](#report)
   - [Visualization](#visualization)
10. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
11. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのメトリクス・分析機能で使用される型定義。使用状況、パフォーマンス、システムヘルス、ビジネス分析などの測定・分析に関する構造を定義する。AWS Athena、Azure Synapse、Google BigQueryなどのデータウェアハウスサービスとの連携を考慮した設計。

## 基本型定義

### Metric

メトリクスの基本構造：

```typescript
interface Metric {
  // 識別情報
  metric_id: string;                      // メトリクスID（UUID）
  metric_name: string;                    // メトリクス名
  namespace: string;                      // 名前空間（例：AWS/MAKOTO）
  
  // メトリクス情報
  type: MetricType;                       // メトリクスタイプ
  unit: MetricUnit;                       // 単位
  value: number | string;                 // 値
  
  // ディメンション（分析の軸）
  dimensions: {
    tenant_id?: string;                   // テナントID
    user_id?: string;                     // ユーザーID
    service?: string;                     // サービス名
    operation?: string;                   // オペレーション
    environment?: string;                 // 環境（prod/dev/staging）
    region?: string;                      // リージョン
    [key: string]: string | undefined;    // カスタムディメンション
  };
  
  // タイムスタンプ（パーティション用）
  timestamp: string;                      // ISO 8601形式
  year: number;                          // 年（パーティション用）
  month: number;                         // 月（パーティション用）
  day: number;                           // 日（パーティション用）
  hour?: number;                         // 時（パーティション用）
  
  // 統計値
  statistics?: {
    min?: number;                         // 最小値
    max?: number;                         // 最大値
    sum?: number;                         // 合計
    avg?: number;                         // 平均
    count?: number;                       // カウント
    p50?: number;                         // 中央値
    p90?: number;                         // 90パーセンタイル
    p95?: number;                         // 95パーセンタイル
    p99?: number;                         // 99パーセンタイル
    std_dev?: number;                     // 標準偏差
  };
  
  // メタデータ
  metadata?: {
    source?: string;                      // データソース
    collector?: string;                   // 収集エージェント
    version?: string;                     // スキーマバージョン
    tags?: Record<string, string>;        // タグ
    correlation_id?: string;              // 相関ID
    trace_id?: string;                    // トレースID
    span_id?: string;                     // スパンID
  };
  
  // データ品質
  quality?: {
    confidence?: number;                  // 信頼度（0-1）
    is_estimated?: boolean;               // 推定値フラグ
    is_incomplete?: boolean;              // 不完全データフラグ
  };
}

// メトリクスタイプ
type MetricType = 
  | "counter"               // カウンター（累積値）
  | "gauge"                 // ゲージ（瞬間値）
  | "histogram"             // ヒストグラム
  | "summary"               // サマリー
  | "rate"                  // レート
  | "percentage";           // パーセンテージ

// メトリクス単位
type MetricUnit = 
  | "count"                 // カウント
  | "bytes"                 // バイト
  | "milliseconds"          // ミリ秒
  | "seconds"               // 秒
  | "percent"               // パーセント
  | "requests"              // リクエスト
  | "operations"            // オペレーション
  | "connections"           // 接続数
  | "threads"               // スレッド数
  | "none";                 // 単位なし
```

### MetricEvent

メトリクスイベント（Athena/Synapse向けスキーマ）：

```typescript
// データレイク用のフラット化されたイベント構造
interface MetricEvent {
  // パーティションキー（S3/ADLS用）
  partition_year: number;                 // 年パーティション
  partition_month: number;                // 月パーティション
  partition_day: number;                  // 日パーティション
  partition_hour?: number;                // 時パーティション
  
  // イベント基本情報
  event_id: string;                       // イベントID（重複排除用）
  event_time: bigint;                     // エポックミリ秒
  event_timestamp: string;                // タイムスタンプ（ISO 8601）
  event_type: string;                     // イベントタイプ
  event_version: string;                  // イベントバージョン
  
  // ビジネスコンテキスト
  tenant_id: string;                      // テナントID
  user_id?: string;                       // ユーザーID
  session_id?: string;                    // セッションID
  request_id?: string;                    // リクエストID
  
  // メトリクス値（フラット化）
  metric_name: string;                    // メトリクス名
  metric_value_double?: number;           // 数値（浮動小数点）
  metric_value_long?: bigint;             // 数値（整数）
  metric_value_string?: string;           // 文字列値
  metric_unit?: string;                   // 単位
  
  // ディメンション（フラット化）
  dim_service?: string;                   // サービス
  dim_operation?: string;                 // オペレーション
  dim_environment?: string;               // 環境
  dim_region?: string;                    // リージョン
  dim_status?: string;                    // ステータス
  dim_error_code?: string;                // エラーコード
  
  // カスタムディメンション（JSON文字列）
  custom_dimensions?: string;             // JSON形式
  
  // メタデータ（JSON文字列）
  metadata?: string;                      // JSON形式
  
  // データ形式情報
  file_format?: "parquet" | "orc" | "json" | "csv";
  compression?: "snappy" | "gzip" | "lz4" | "zstd";
}
```

### DataPoint

データポイント：

```typescript
interface DataPoint {
  // 時系列情報
  timestamp: string;                      // タイムスタンプ
  epoch_ms: number;                       // エポックミリ秒
  
  // 値
  value: number | string | boolean | null; // 値
  
  // 品質指標
  quality?: {
    is_valid: boolean;                    // 有効フラグ
    is_outlier?: boolean;                 // 外れ値フラグ
    confidence?: number;                  // 信頼度
  };
  
  // アノテーション
  annotations?: {
    event?: string;                       // イベント
    note?: string;                        // メモ
    tags?: string[];                      // タグ
  };
}
```

### TimeSeries

時系列データ：

```typescript
interface TimeSeries {
  // 識別情報
  series_id: string;                      // シリーズID
  metric_name: string;                    // メトリクス名
  
  // 時間範囲
  time_range: {
    start: string;                        // 開始時刻
    end: string;                          // 終了時刻
    interval?: string;                    // 間隔（1m, 5m, 1h等）
    timezone?: string;                    // タイムゾーン
  };
  
  // データポイント
  data_points: DataPoint[];               // データポイント配列
  
  // 集約情報
  aggregation?: {
    method: AggregationMethod;            // 集約方法
    window?: string;                      // ウィンドウサイズ
    fill_missing?: "null" | "zero" | "previous" | "interpolate";
  };
  
  // 統計サマリー
  summary?: {
    count: number;                        // データポイント数
    min: number;                          // 最小値
    max: number;                          // 最大値
    avg: number;                          // 平均値
    sum: number;                          // 合計
    std_dev?: number;                     // 標準偏差
  };
}

// 集約方法
type AggregationMethod = 
  | "sum"
  | "avg"
  | "min"
  | "max"
  | "count"
  | "first"
  | "last"
  | "median"
  | "percentile";
```

## 使用状況メトリクス型定義

### UsageMetrics

使用状況メトリクス：

```typescript
interface UsageMetrics {
  // 期間
  period: {
    start_date: string;                   // 開始日
    end_date: string;                     // 終了日
    granularity: "hour" | "day" | "week" | "month";
  };
  
  // API使用状況
  api_usage: APIUsage;                    // API使用状況
  
  // ユーザーアクティビティ
  user_activity: UserActivity;            // ユーザーアクティビティ
  
  // リソース消費
  resource_consumption: ResourceConsumption; // リソース消費
  
  // 機能使用状況
  feature_usage: {
    [feature_name: string]: {
      usage_count: number;                // 使用回数
      unique_users: number;               // ユニークユーザー数
      total_duration_ms?: number;        // 総使用時間
      success_rate?: number;             // 成功率
    };
  };
  
  // コスト
  cost?: {
    compute_cost: number;                 // 計算コスト
    storage_cost: number;                 // ストレージコスト
    network_cost: number;                 // ネットワークコスト
    total_cost: number;                   // 総コスト
    currency: string;                     // 通貨
  };
}
```

### APIUsage

API使用状況：

```typescript
interface APIUsage {
  // 総計
  total_requests: number;                 // 総リクエスト数
  successful_requests: number;            // 成功リクエスト数
  failed_requests: number;                // 失敗リクエスト数
  
  // エンドポイント別
  by_endpoint: Array<{
    endpoint: string;                     // エンドポイント
    method: string;                       // HTTPメソッド
    count: number;                        // リクエスト数
    avg_response_time_ms: number;        // 平均レスポンス時間
    error_rate: number;                   // エラー率
    
    // ステータスコード分布
    status_codes: {
      "2xx": number;
      "3xx": number;
      "4xx": number;
      "5xx": number;
    };
  }>;
  
  // 時系列データ
  time_series?: Array<{
    timestamp: string;
    requests: number;
    errors: number;
    avg_latency_ms: number;
  }>;
  
  // レート制限
  rate_limiting?: {
    throttled_requests: number;           // スロットルされたリクエスト
    rate_limit_exceeded: number;          // レート制限超過
  };
}
```

### UserActivity

ユーザーアクティビティ：

```typescript
interface UserActivity {
  // アクティブユーザー
  active_users: {
    daily: number;                        // DAU
    weekly: number;                       // WAU
    monthly: number;                      // MAU
  };
  
  // 新規ユーザー
  new_users: {
    count: number;                        // 新規ユーザー数
    growth_rate: number;                  // 成長率
  };
  
  // セッション
  sessions: {
    total_sessions: number;               // 総セッション数
    avg_session_duration_ms: number;     // 平均セッション時間
    bounce_rate: number;                  // バウンス率
    pages_per_session: number;            // セッションあたりページ数
  };
  
  // アクション
  user_actions: Array<{
    action_type: string;                  // アクションタイプ
    count: number;                        // 実行回数
    unique_users: number;                 // ユニークユーザー数
    avg_time_ms?: number;                 // 平均実行時間
  }>;
  
  // ユーザー分布
  user_distribution?: {
    by_country?: Record<string, number>;  // 国別
    by_device?: Record<string, number>;   // デバイス別
    by_browser?: Record<string, number>;  // ブラウザ別
    by_plan?: Record<string, number>;     // プラン別
  };
}
```

### ResourceConsumption

リソース消費：

```typescript
interface ResourceConsumption {
  // ストレージ
  storage: {
    total_bytes: number;                  // 総使用量
    files_count: number;                  // ファイル数
    
    by_type?: {
      images: number;                     // 画像
      documents: number;                  // ドキュメント
      audio: number;                      // 音声
      video: number;                      // 動画
      other: number;                      // その他
    };
    
    growth_rate?: number;                 // 成長率
  };
  
  // 帯域幅
  bandwidth: {
    ingress_bytes: number;                // 受信バイト数
    egress_bytes: number;                 // 送信バイト数
    peak_bandwidth_mbps?: number;        // ピーク帯域幅
  };
  
  // コンピュート
  compute: {
    total_compute_hours: number;          // 総計算時間
    
    by_service?: {
      chat: number;                       // チャット
      image_generation: number;           // 画像生成
      audio_processing: number;           // 音声処理
      web_crawling: number;               // Webクロール
    };
    
    // Lambda/Functions使用
    serverless?: {
      invocations: number;                // 呼び出し回数
      duration_ms: number;                // 実行時間
      memory_mb_ms: number;               // メモリ使用量
    };
  };
  
  // データベース
  database?: {
    read_units: number;                   // 読み取りユニット
    write_units: number;                  // 書き込みユニット
    storage_gb: number;                   // ストレージ
    iops?: number;                        // IOPS
  };
}
```

## パフォーマンスメトリクス型定義

### PerformanceMetrics

パフォーマンスメトリクス：

```typescript
interface PerformanceMetrics {
  // レスポンスタイム
  response_time: ResponseTime;            // レスポンスタイム
  
  // スループット
  throughput: Throughput;                 // スループット
  
  // レイテンシ
  latency: Latency;                       // レイテンシ
  
  // エラー率
  error_rate: {
    overall: number;                      // 全体エラー率
    by_type: Record<string, number>;      // タイプ別エラー率
    by_service: Record<string, number>;   // サービス別エラー率
  };
  
  // SLA
  sla?: {
    availability: number;                 // 可用性（%）
    uptime: number;                       // アップタイム（秒）
    downtime: number;                     // ダウンタイム（秒）
    sla_breaches?: number;                // SLA違反回数
  };
  
  // パフォーマンス分布
  performance_distribution?: {
    percentiles: {
      p50: number;
      p75: number;
      p90: number;
      p95: number;
      p99: number;
      p999: number;
    };
    histogram?: Array<{
      bucket: string;
      count: number;
    }>;
  };
}
```

### ResponseTime

レスポンスタイム：

```typescript
interface ResponseTime {
  // 統計値
  min_ms: number;                         // 最小値
  max_ms: number;                         // 最大値
  avg_ms: number;                         // 平均値
  median_ms: number;                      // 中央値
  
  // パーセンタイル
  percentiles: {
    p50: number;
    p90: number;
    p95: number;
    p99: number;
  };
  
  // サービス別
  by_service?: Array<{
    service: string;
    avg_ms: number;
    p95_ms: number;
    sample_count: number;
  }>;
  
  // 時系列
  time_series?: Array<{
    timestamp: string;
    value: number;
    sample_count: number;
  }>;
  
  // 閾値違反
  threshold_violations?: {
    count: number;                        // 違反回数
    threshold_ms: number;                 // 閾値
    violation_rate: number;               // 違反率
  };
}
```

### Throughput

スループット：

```typescript
interface Throughput {
  // リクエスト/秒
  requests_per_second: {
    current: number;                      // 現在値
    avg: number;                          // 平均
    peak: number;                         // ピーク
  };
  
  // データ転送
  data_transfer: {
    bytes_per_second: number;             // バイト/秒
    messages_per_second?: number;         // メッセージ/秒
    operations_per_second?: number;       // オペレーション/秒
  };
  
  // 同時接続
  concurrent_connections: {
    current: number;
    avg: number;
    peak: number;
  };
  
  // キャパシティ
  capacity?: {
    current_utilization: number;          // 現在の使用率（%）
    max_capacity: number;                 // 最大キャパシティ
    scaling_events?: number;              // スケーリングイベント数
  };
}
```

### Latency

レイテンシ：

```typescript
interface Latency {
  // ネットワークレイテンシ
  network: {
    avg_ms: number;
    p95_ms: number;
    packet_loss_rate?: number;           // パケットロス率
  };
  
  // データベースレイテンシ
  database: {
    read_latency_ms: number;
    write_latency_ms: number;
    connection_pool_wait_ms?: number;
  };
  
  // キャッシュレイテンシ
  cache?: {
    hit_latency_ms: number;
    miss_latency_ms: number;
    hit_rate: number;
  };
  
  // 外部API レイテンシ
  external_api?: Array<{
    api_name: string;
    avg_latency_ms: number;
    p95_latency_ms: number;
    timeout_rate: number;
  }>;
  
  // エンドツーエンド
  end_to_end: {
    avg_ms: number;
    p95_ms: number;
    breakdown?: {                        // 内訳
      network_ms: number;
      processing_ms: number;
      database_ms: number;
      other_ms: number;
    };
  };
}
```

## システムヘルスメトリクス型定義

### SystemHealth

システムヘルス：

```typescript
interface SystemHealth {
  // 全体ステータス
  overall_status: HealthStatus;           // 全体ステータス
  health_score: number;                   // ヘルススコア（0-100）
  
  // リソースメトリクス
  resources: ResourceMetrics;             // リソースメトリクス
  
  // サービスヘルス
  services: ServiceHealth[];              // サービスヘルス
  
  // アラート
  active_alerts?: Array<{
    alert_id: string;
    severity: "info" | "warning" | "error" | "critical";
    message: string;
    triggered_at: string;
  }>;
  
  // 依存関係
  dependencies?: Array<{
    name: string;
    type: string;
    status: HealthStatus;
    latency_ms?: number;
  }>;
  
  // 最終チェック
  last_check: {
    timestamp: string;
    duration_ms: number;
    checks_performed: number;
    checks_failed: number;
  };
}

// ヘルスステータス
type HealthStatus = 
  | "healthy"
  | "degraded"
  | "unhealthy"
  | "unknown";
```

### ResourceMetrics

リソースメトリクス：

```typescript
interface ResourceMetrics {
  // CPU
  cpu: {
    usage_percent: number;                // 使用率（%）
    cores_used: number;                   // 使用コア数
    total_cores: number;                  // 総コア数
    
    by_process?: Array<{
      process_name: string;
      cpu_percent: number;
    }>;
    
    temperature_celsius?: number;         // 温度
    throttling?: boolean;                 // スロットリング
  };
  
  // メモリ
  memory: {
    used_bytes: number;                   // 使用量
    total_bytes: number;                  // 総容量
    usage_percent: number;                // 使用率（%）
    
    breakdown?: {
      heap_bytes: number;
      stack_bytes: number;
      cache_bytes: number;
      buffer_bytes: number;
    };
    
    swap?: {
      used_bytes: number;
      total_bytes: number;
    };
  };
  
  // ディスク
  disk: {
    used_bytes: number;
    total_bytes: number;
    usage_percent: number;
    
    iops?: {
      read_iops: number;
      write_iops: number;
    };
    
    throughput?: {
      read_mbps: number;
      write_mbps: number;
    };
    
    by_partition?: Array<{
      mount_point: string;
      used_bytes: number;
      total_bytes: number;
    }>;
  };
  
  // ネットワーク
  network: {
    bandwidth: {
      ingress_mbps: number;
      egress_mbps: number;
    };
    
    packets: {
      received: number;
      sent: number;
      dropped: number;
      errors: number;
    };
    
    connections: {
      active: number;
      established: number;
      time_wait: number;
    };
  };
}
```

### ServiceHealth

サービスヘルス：

```typescript
interface ServiceHealth {
  // サービス情報
  service_name: string;                   // サービス名
  service_type: string;                   // サービスタイプ
  version?: string;                       // バージョン
  
  // ステータス
  status: HealthStatus;                   // ステータス
  uptime_seconds: number;                 // アップタイム
  
  // メトリクス
  metrics: {
    request_rate?: number;                // リクエストレート
    error_rate?: number;                  // エラー率
    avg_response_time_ms?: number;        // 平均レスポンス時間
    active_connections?: number;          // アクティブ接続数
  };
  
  // インスタンス
  instances?: Array<{
    instance_id: string;
    status: HealthStatus;
    cpu_percent?: number;
    memory_percent?: number;
    last_heartbeat?: string;
  }>;
  
  // ヘルスチェック
  health_checks?: Array<{
    check_name: string;
    status: "pass" | "fail";
    message?: string;
    last_check: string;
  }>;
}
```

## ビジネス分析型定義

### BusinessAnalytics

ビジネス分析：

```typescript
interface BusinessAnalytics {
  // 期間
  period: {
    start_date: string;
    end_date: string;
  };
  
  // ユーザーエンゲージメント
  user_engagement: UserEngagement;        // ユーザーエンゲージメント
  
  // コンバージョン
  conversion: ConversionMetrics;          // コンバージョンメトリクス
  
  // リテンション
  retention: RetentionMetrics;            // リテンションメトリクス
  
  // 収益
  revenue?: {
    total_revenue: number;                // 総収益
    mrr?: number;                         // MRR（月次定期収益）
    arr?: number;                         // ARR（年次定期収益）
    arpu?: number;                        // ARPU（ユーザーあたり収益）
    ltv?: number;                         // LTV（顧客生涯価値）
    
    by_plan?: Record<string, number>;     // プラン別
    by_country?: Record<string, number>;  // 国別
    
    growth?: {
      month_over_month: number;           // 月次成長率
      year_over_year: number;             // 年次成長率
    };
  };
  
  // チャーン
  churn?: {
    churn_rate: number;                   // チャーン率
    churned_users: number;                // 解約ユーザー数
    churn_revenue: number;                // 解約による収益損失
    
    reasons?: Array<{
      reason: string;
      count: number;
      percentage: number;
    }>;
  };
}
```

### UserEngagement

ユーザーエンゲージメント：

```typescript
interface UserEngagement {
  // エンゲージメント率
  engagement_rate: number;                // エンゲージメント率
  
  // アクティビティ
  activities: {
    total_actions: number;                // 総アクション数
    actions_per_user: number;             // ユーザーあたりアクション
    
    by_type: Array<{
      activity_type: string;
      count: number;
      unique_users: number;
      engagement_rate: number;
    }>;
  };
  
  // セッション深度
  session_depth: {
    avg_session_duration_minutes: number; // 平均セッション時間
    avg_pages_per_session: number;        // セッションあたりページ数
    bounce_rate: number;                  // バウンス率
    
    distribution: Array<{
      duration_range: string;              // 時間範囲
      session_count: number;
      percentage: number;
    }>;
  };
  
  // 機能利用
  feature_adoption: {
    [feature_name: string]: {
      adoption_rate: number;              // 採用率
      usage_frequency: number;            // 使用頻度
      time_to_adopt_days?: number;        // 採用までの日数
    };
  };
  
  // コホート分析
  cohort_analysis?: Array<{
    cohort_date: string;
    cohort_size: number;
    retention_rates: number[];            // 各期間のリテンション率
  }>;
}
```

### ConversionMetrics

コンバージョンメトリクス：

```typescript
interface ConversionMetrics {
  // ファネル
  funnel: Array<{
    stage_name: string;                   // ステージ名
    users_entered: number;                // 流入ユーザー数
    users_converted: number;              // コンバージョンユーザー数
    conversion_rate: number;              // コンバージョン率
    avg_time_to_convert_hours?: number;  // コンバージョンまでの時間
    
    drop_off_rate?: number;               // 離脱率
    drop_off_reasons?: string[];          // 離脱理由
  }>;
  
  // 目標達成
  goals: Array<{
    goal_name: string;                    // 目標名
    completions: number;                  // 完了数
    completion_rate: number;              // 完了率
    value?: number;                       // 価値
  }>;
  
  // A/Bテスト
  ab_tests?: Array<{
    test_name: string;
    variant_a: {
      users: number;
      conversions: number;
      conversion_rate: number;
    };
    variant_b: {
      users: number;
      conversions: number;
      conversion_rate: number;
    };
    statistical_significance?: number;    // 統計的有意性
    winner?: "A" | "B" | "inconclusive";
  }>;
}
```

### RetentionMetrics

リテンションメトリクス：

```typescript
interface RetentionMetrics {
  // リテンション率
  retention_rates: {
    day_1: number;                        // 1日後
    day_7: number;                        // 7日後
    day_30: number;                       // 30日後
    day_90: number;                       // 90日後
  };
  
  // リテンションカーブ
  retention_curve: Array<{
    day: number;
    retention_rate: number;
    active_users: number;
  }>;
  
  // 定着指標
  stickiness: {
    dau_mau_ratio: number;                // DAU/MAU比率
    wau_mau_ratio: number;                // WAU/MAU比率
  };
  
  // リピート率
  repeat_usage: {
    repeat_rate: number;                  // リピート率
    avg_days_between_visits: number;      // 平均訪問間隔
    
    frequency_distribution: Array<{
      visits_per_period: string;
      user_count: number;
      percentage: number;
    }>;
  };
  
  // 復帰率
  resurrection?: {
    resurrected_users: number;            // 復帰ユーザー数
    resurrection_rate: number;            // 復帰率
    avg_dormant_period_days: number;      // 平均休眠期間
  };
}
```

## データウェアハウス連携型定義

### AthenaQuery

AWS Athena クエリ定義：

```typescript
interface AthenaQuery {
  // クエリ情報
  query_id?: string;                      // クエリID
  query_string: string;                   // SQLクエリ
  database: string;                       // データベース名
  
  // S3設定
  s3_output_location: string;             // 出力先S3パス
  s3_source_location?: string;            // ソースデータS3パス
  
  // テーブル定義（CREATE TABLE用）
  table_definition?: {
    table_name: string;
    columns: Array<{
      name: string;
      type: AthenaDataType;
      comment?: string;
    }>;
    partition_keys?: Array<{
      name: string;
      type: string;
    }>;
    storage_format: "PARQUET" | "ORC" | "JSON" | "CSV";
    compression?: "SNAPPY" | "GZIP" | "LZO" | "ZSTD";
    location: string;                     // S3ロケーション
  };
  
  // クエリ実行設定
  execution_config?: {
    workgroup?: string;                   // ワークグループ
    result_configuration?: {
      encryption?: {
        type: "SSE_S3" | "SSE_KMS" | "CSE_KMS";
        kms_key?: string;
      };
    };
    max_execution_time_seconds?: number;
  };
  
  // パフォーマンス統計
  statistics?: {
    data_scanned_bytes?: number;
    execution_time_ms?: number;
    query_queue_time_ms?: number;
    service_processing_time_ms?: number;
  };
}

// Athenaデータ型
type AthenaDataType = 
  | "boolean"
  | "tinyint" | "smallint" | "int" | "bigint"
  | "float" | "double" | "decimal"
  | "string" | "varchar" | "char"
  | "date" | "timestamp"
  | "array" | "map" | "struct"
  | "binary";
```

### SynapseQuery

Azure Synapse クエリ定義：

```typescript
interface SynapseQuery {
  // クエリ情報
  query_id?: string;
  query_text: string;
  database: string;
  schema?: string;
  
  // データレイク設定
  data_lake: {
    account_name: string;                 // ストレージアカウント
    container: string;                    // コンテナー
    folder_path: string;                  // フォルダパス
    file_format: "PARQUET" | "DELTA" | "CSV" | "JSON";
  };
  
  // 外部テーブル定義
  external_table?: {
    table_name: string;
    columns: Array<{
      name: string;
      type: SynapseDataType;
      nullable?: boolean;
    }>;
    location: string;
    data_source: string;
    file_format: string;
  };
  
  // SQLプール設定
  sql_pool?: {
    name: string;
    type: "dedicated" | "serverless";
    performance_level?: string;           // DWU設定
  };
  
  // 実行オプション
  execution_options?: {
    label?: string;                       // クエリラベル
    resource_class?: string;              // リソースクラス
    result_set_caching?: boolean;         // 結果セットキャッシング
    distributed_query?: boolean;          // 分散クエリ
  };
  
  // 統計情報
  statistics?: {
    rows_processed?: number;
    data_processed_gb?: number;
    duration_seconds?: number;
    dpu_seconds?: number;                 // データ処理単位秒
  };
}

// Synapseデータ型
type SynapseDataType = 
  | "bit"
  | "tinyint" | "smallint" | "int" | "bigint"
  | "float" | "real"
  | "decimal" | "numeric"
  | "money" | "smallmoney"
  | "char" | "varchar" | "nchar" | "nvarchar"
  | "date" | "datetime" | "datetime2" | "smalldatetime"
  | "uniqueidentifier"
  | "binary" | "varbinary";
```

### BigQueryIntegration

Google BigQuery 統合：

```typescript
interface BigQueryIntegration {
  // データセット
  dataset: {
    project_id: string;
    dataset_id: string;
    location: string;
  };
  
  // テーブル定義
  table: {
    table_id: string;
    schema: Array<{
      name: string;
      type: BigQueryDataType;
      mode: "NULLABLE" | "REQUIRED" | "REPEATED";
      description?: string;
    }>;
    
    partitioning?: {
      type: "TIME" | "RANGE" | "INTEGER";
      field: string;
      expiration_days?: number;
    };
    
    clustering?: {
      fields: string[];
    };
  };
  
  // ストリーミング挿入
  streaming?: {
    insert_id?: string;
    rows: Array<{
      json: Record<string, any>;
      insert_id?: string;
    }>;
  };
  
  // バッチロード
  batch_load?: {
    source_uris: string[];                // GCS URIs
    source_format: "CSV" | "JSON" | "PARQUET" | "ORC" | "AVRO";
    write_disposition: "WRITE_TRUNCATE" | "WRITE_APPEND" | "WRITE_EMPTY";
    create_disposition: "CREATE_IF_NEEDED" | "CREATE_NEVER";
  };
  
  // クエリ設定
  query_config?: {
    use_query_cache?: boolean;
    use_legacy_sql?: boolean;
    maximum_bytes_billed?: bigint;
    priority?: "INTERACTIVE" | "BATCH";
  };
}

// BigQueryデータ型
type BigQueryDataType = 
  | "INT64" | "FLOAT64" | "NUMERIC" | "BIGNUMERIC"
  | "BOOL"
  | "STRING" | "BYTES"
  | "DATE" | "DATETIME" | "TIME" | "TIMESTAMP"
  | "STRUCT" | "ARRAY"
  | "GEOGRAPHY" | "JSON";
```

### ParquetSchema

Parquet スキーマ定義：

```typescript
interface ParquetSchema {
  // スキーマ情報
  schema_name: string;
  version: string;
  
  // カラム定義
  columns: Array<{
    name: string;
    type: ParquetType;
    encoding?: ParquetEncoding;
    compression?: ParquetCompression;
    nullable?: boolean;
    
    // 統計情報
    statistics?: {
      null_count?: number;
      distinct_count?: number;
      min_value?: any;
      max_value?: any;
    };
  }>;
  
  // 行グループ設定
  row_group_size?: number;                // 行グループサイズ
  page_size?: number;                     // ページサイズ
  
  // メタデータ
  metadata?: {
    created_by?: string;
    created_time?: string;
    key_value_metadata?: Record<string, string>;
  };
  
  // パーティション
  partitioning?: {
    scheme: "hive" | "directory";
    columns: string[];
  };
}

// Parquet型
type ParquetType = 
  | "BOOLEAN"
  | "INT32" | "INT64" | "INT96"
  | "FLOAT" | "DOUBLE"
  | "BYTE_ARRAY" | "FIXED_LEN_BYTE_ARRAY"
  | "UTF8" | "ENUM" | "UUID"
  | "DATE" | "TIME_MILLIS" | "TIME_MICROS"
  | "TIMESTAMP_MILLIS" | "TIMESTAMP_MICROS"
  | "LIST" | "MAP" | "STRUCT";

// Parquetエンコーディング
type ParquetEncoding = 
  | "PLAIN"
  | "PLAIN_DICTIONARY"
  | "RLE"
  | "BIT_PACKED"
  | "DELTA_BINARY_PACKED"
  | "DELTA_LENGTH_BYTE_ARRAY"
  | "DELTA_BYTE_ARRAY";

// Parquet圧縮
type ParquetCompression = 
  | "UNCOMPRESSED"
  | "SNAPPY"
  | "GZIP"
  | "LZO"
  | "BROTLI"
  | "LZ4"
  | "ZSTD";
```

## リアルタイム監視型定義

### RealtimeMonitoring

リアルタイム監視：

```typescript
interface RealtimeMonitoring {
  // 監視設定
  monitoring_id: string;                  // 監視ID
  name: string;                           // 監視名
  enabled: boolean;                       // 有効/無効
  
  // 監視対象
  targets: Array<{
    type: "metric" | "log" | "trace" | "event";
    source: string;                       // ソース
    filter?: string;                      // フィルタ条件
  }>;
  
  // ストリーミング設定
  streaming: StreamingMetrics;            // ストリーミングメトリクス
  
  // アラート設定
  alerts: AlertConfiguration[];           // アラート設定
  
  // ダッシュボード
  dashboard?: {
    dashboard_id: string;
    auto_refresh: boolean;
    refresh_interval_seconds?: number;
  };
  
  // データ保持
  retention?: {
    raw_data_days: number;                // 生データ保持期間
    aggregated_data_days: number;         // 集約データ保持期間
  };
}
```

### AlertConfiguration

アラート設定：

```typescript
interface AlertConfiguration {
  // アラート情報
  alert_id: string;                       // アラートID
  name: string;                           // アラート名
  description?: string;                   // 説明
  severity: "info" | "warning" | "error" | "critical";
  
  // 条件
  condition: {
    metric: string;                       // メトリクス名
    operator: ComparisonOperator;         // 比較演算子
    threshold: number;                    // 閾値
    
    evaluation_period?: {
      window_minutes: number;              // 評価ウィンドウ
      frequency_minutes: number;          // 評価頻度
      datapoints_to_alarm: number;        // アラーム発生データポイント数
    };
    
    aggregation?: {
      method: AggregationMethod;
      dimensions?: string[];
    };
  };
  
  // アクション
  actions: Array<{
    type: "email" | "sms" | "slack" | "webhook" | "lambda";
    target: string;                       // 送信先
    
    throttle?: {
      enabled: boolean;
      period_minutes: number;              // スロットル期間
    };
  }>;
  
  // 状態
  state?: {
    current_state: "OK" | "ALARM" | "INSUFFICIENT_DATA";
    last_state_change?: string;
    last_notification?: string;
  };
}

// 比較演算子
type ComparisonOperator = 
  | "GreaterThanThreshold"
  | "LessThanThreshold"
  | "GreaterThanOrEqualToThreshold"
  | "LessThanOrEqualToThreshold"
  | "NotEqualToThreshold"
  | "GreaterThanUpperThreshold"
  | "LessThanLowerThreshold";
```

### StreamingMetrics

ストリーミングメトリクス：

```typescript
interface StreamingMetrics {
  // ストリーム情報
  stream_name: string;                    // ストリーム名
  stream_type: "kinesis" | "kafka" | "eventbridge" | "pubsub";
  
  // データフロー
  data_flow: {
    ingestion_rate: number;               // 取り込みレート（/秒）
    processing_rate: number;              // 処理レート（/秒）
    
    lag?: {
      current_lag_ms: number;             // 現在の遅延
      max_lag_ms: number;                 // 最大遅延
    };
    
    buffer?: {
      size: number;                       // バッファサイズ
      utilization_percent: number;        // 使用率
    };
  };
  
  // ウィンドウ処理
  windowing?: {
    type: "tumbling" | "sliding" | "session";
    size_seconds: number;
    
    aggregations?: Array<{
      function: AggregationMethod;
      field: string;
      output_field: string;
    }>;
  };
  
  // 出力先
  sinks: Array<{
    type: "s3" | "dynamodb" | "elasticsearch" | "custom";
    destination: string;
    format?: "json" | "parquet" | "avro";
    batch_size?: number;
    batch_interval_seconds?: number;
  }>;
}
```

## ダッシュボード・レポート型定義

### Dashboard

ダッシュボード：

```typescript
interface Dashboard {
  // ダッシュボード情報
  dashboard_id: string;                   // ダッシュボードID
  name: string;                           // ダッシュボード名
  description?: string;                   // 説明
  
  // レイアウト
  layout: {
    type: "grid" | "flex" | "fixed";
    columns?: number;                     // カラム数
    rows?: number;                        // 行数
  };
  
  // ウィジェット
  widgets: Array<{
    widget_id: string;
    type: WidgetType;
    title: string;
    
    position: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
    
    visualization: Visualization;         // ビジュアライゼーション
    
    data_source: {
      metric?: string;
      query?: string;
      time_range?: string;
      refresh_interval?: number;
    };
    
    settings?: Record<string, any>;
  }>;
  
  // フィルタ
  filters?: Array<{
    name: string;
    type: "dropdown" | "date_range" | "text";
    default_value?: any;
    options?: any[];
  }>;
  
  // 共有設定
  sharing?: {
    visibility: "private" | "team" | "public";
    shared_with?: string[];               // ユーザー/グループID
    embed_enabled?: boolean;
  };
  
  // 更新設定
  refresh?: {
    auto_refresh: boolean;
    interval_seconds?: number;
    last_refresh?: string;
  };
}

// ウィジェットタイプ
type WidgetType = 
  | "metric"          // 単一メトリクス
  | "chart"           // チャート
  | "table"           // テーブル
  | "heatmap"         // ヒートマップ
  | "gauge"           // ゲージ
  | "map"             // 地図
  | "text"            // テキスト
  | "custom";         // カスタム
```

### Report

レポート：

```typescript
interface Report {
  // レポート情報
  report_id: string;                      // レポートID
  name: string;                           // レポート名
  type: ReportType;                       // レポートタイプ
  
  // スケジュール
  schedule?: {
    enabled: boolean;
    frequency: "daily" | "weekly" | "monthly" | "quarterly";
    time?: string;                        // 実行時刻
    timezone?: string;                    // タイムゾーン
    
    recipients?: Array<{
      email?: string;
      slack_channel?: string;
    }>;
  };
  
  // コンテンツ
  sections: Array<{
    section_id: string;
    title: string;
    type: "summary" | "detail" | "chart" | "table";
    
    content?: {
      text?: string;
      metrics?: Array<{
        name: string;
        value: any;
        change?: number;
      }>;
      visualization?: Visualization;
    };
    
    data_source?: {
      query?: string;
      time_range?: string;
    };
  }>;
  
  // 出力形式
  output_format: {
    format: "pdf" | "excel" | "html" | "csv";
    template?: string;                    // テンプレート
    
    styling?: {
      logo?: string;
      colors?: Record<string, string>;
      fonts?: Record<string, string>;
    };
  };
  
  // 配信設定
  delivery?: {
    method: "email" | "s3" | "sftp" | "api";
    destination?: string;
    
    encryption?: {
      enabled: boolean;
      method?: string;
    };
  };
}

// レポートタイプ
type ReportType = 
  | "executive"       // エグゼクティブサマリー
  | "operational"     // オペレーショナル
  | "analytical"      // 分析
  | "compliance"      // コンプライアンス
  | "custom";         // カスタム
```

### Visualization

ビジュアライゼーション：

```typescript
interface Visualization {
  // ビジュアライゼーションタイプ
  type: VisualizationType;
  
  // チャート設定
  chart_config?: {
    chart_type?: "line" | "bar" | "pie" | "scatter" | "area" | "combo";
    
    axes?: {
      x?: AxisConfig;
      y?: AxisConfig;
      y2?: AxisConfig;                    // 第2Y軸
    };
    
    series?: Array<{
      name: string;
      data_field: string;
      type?: string;
      color?: string;
      axis?: "y" | "y2";
    }>;
    
    legend?: {
      enabled: boolean;
      position?: "top" | "bottom" | "left" | "right";
    };
    
    annotations?: Array<{
      type: "line" | "box" | "text";
      value?: any;
      text?: string;
      color?: string;
    }>;
  };
  
  // データ設定
  data_config?: {
    aggregation?: AggregationMethod;
    group_by?: string[];
    order_by?: Array<{
      field: string;
      direction: "asc" | "desc";
    }>;
    limit?: number;
  };
  
  // スタイル
  style?: {
    color_scheme?: string;
    theme?: "light" | "dark";
    custom_css?: string;
  };
  
  // インタラクション
  interaction?: {
    zoom?: boolean;
    pan?: boolean;
    hover?: boolean;
    click?: boolean;
    export?: boolean;
  };
}

// ビジュアライゼーションタイプ
type VisualizationType = 
  | "line_chart"
  | "bar_chart"
  | "pie_chart"
  | "scatter_plot"
  | "heatmap"
  | "gauge"
  | "number"
  | "table"
  | "map";

// 軸設定
interface AxisConfig {
  label?: string;
  type?: "linear" | "logarithmic" | "category" | "datetime";
  min?: number;
  max?: number;
  format?: string;
}
```

## API リクエスト/レスポンス型定義

### メトリクス取得

```typescript
// メトリクス取得リクエスト
interface GetMetricsRequest {
  // メトリクス指定
  metric_names?: string[];                // メトリクス名
  namespace?: string;                     // 名前空間
  
  // フィルタ
  dimensions?: Record<string, string>;    // ディメンション
  
  // 時間範囲
  time_range: {
    start: string;                        // 開始時刻
    end: string;                          // 終了時刻
  };
  
  // 集約
  aggregation?: {
    method: AggregationMethod;
    period_seconds?: number;              // 集約期間
  };
  
  // ページネーション
  pagination?: {
    limit?: number;
    next_token?: string;
  };
}

// メトリクス取得レスポンス
interface GetMetricsResponse {
  metrics: Metric[];                      // メトリクス配列
  
  time_series?: TimeSeries[];             // 時系列データ
  
  pagination?: {
    next_token?: string;
    has_more: boolean;
  };
}
```

### クエリ実行

```typescript
// データウェアハウスクエリ実行リクエスト
interface ExecuteQueryRequest {
  // クエリ
  query: string;                          // SQLクエリ（必須）
  
  // プラットフォーム
  platform: "athena" | "synapse" | "bigquery";
  
  // データベース
  database?: string;
  schema?: string;
  
  // パラメータ
  parameters?: Record<string, any>;
  
  // 実行オプション
  options?: {
    async?: boolean;                      // 非同期実行
    timeout_seconds?: number;              // タイムアウト
    max_rows?: number;                    // 最大行数
  };
}

// クエリ実行レスポンス
interface ExecuteQueryResponse {
  query_id: string;                       // クエリID
  
  // 同期実行の場合
  results?: {
    columns: Array<{
      name: string;
      type: string;
    }>;
    rows: any[][];
    row_count: number;
  };
  
  // 非同期実行の場合
  status?: "running" | "succeeded" | "failed";
  result_location?: string;               // 結果格納場所
  
  // 統計
  statistics?: {
    data_scanned_bytes?: number;
    execution_time_ms?: number;
    cost?: number;
  };
}
```

### レポート生成

```typescript
// レポート生成リクエスト
interface GenerateReportRequest {
  report_id?: string;                     // 既存レポートID
  
  // レポート定義
  report?: {
    type: ReportType;
    time_range: {
      start: string;
      end: string;
    };
    
    metrics?: string[];                   // 含めるメトリクス
    dimensions?: string[];                 // グループ化ディメンション
    
    format: "pdf" | "excel" | "html";
  };
  
  // 配信オプション
  delivery?: {
    email?: string;
    include_raw_data?: boolean;
  };
}

// レポート生成レスポンス
interface GenerateReportResponse {
  report_id: string;                      // レポートID
  status: "generating" | "completed" | "failed";
  
  download_url?: string;                  // ダウンロードURL
  expires_at?: string;                    // URL有効期限
  
  summary?: {
    pages?: number;
    file_size_bytes?: number;
    generation_time_seconds?: number;
  };
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - 基本型定義（Metric、MetricEvent、DataPoint、TimeSeries）
  - AWS Athena/Azure Synapse/BigQuery向けのスキーマ設計
  - Parquet形式でのデータレイク保存を考慮した型定義
  - 使用状況メトリクス型定義
  - パフォーマンスメトリクス型定義
  - システムヘルスメトリクス型定義
  - ビジネス分析型定義
  - データウェアハウス連携型定義
  - リアルタイム監視型定義
  - ダッシュボード・レポート型定義
  - API リクエスト/レスポンス型定義