# 監査ログAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [AuditLog](#auditlog)
   - [AuditEvent](#auditevent)
   - [AuditContext](#auditcontext)
3. [ログカテゴリ型定義](#ログカテゴリ型定義)
   - [AccessLog](#accesslog)
   - [OperationLog](#operationlog)
   - [DataChangeLog](#datachangelog)
   - [SecurityLog](#securitylog)
4. [検索・フィルタ型定義](#検索フィルタ型定義)
   - [AuditLogQuery](#auditlogquery)
   - [AuditLogFilter](#auditlogfilter)
5. [集計・分析型定義](#集計分析型定義)
   - [AuditStatistics](#auditstatistics)
   - [AuditReport](#auditreport)
6. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [ログ記録](#ログ記録)
   - [ログ検索](#ログ検索)
   - [ログエクスポート](#ログエクスポート)
   - [コンプライアンスレポート](#コンプライアンスレポート)
7. [保持ポリシー型定義](#保持ポリシー型定義)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの監査ログ機能で使用される型定義。システム内のすべての操作、アクセス、データ変更を記録し、セキュリティ監査とコンプライアンス要件を満たすための構造を定義する。

## 基本型定義

### AuditLog

監査ログの基本構造：

```typescript
interface AuditLog {
  // 識別情報
  log_id: string;                        // ログID（UUID）
  timestamp: string;                     // 発生日時（ISO 8601、ミリ秒精度）
  
  // イベント情報
  event_type: AuditEventType;            // イベントタイプ
  event_category: AuditEventCategory;    // イベントカテゴリ
  event_name: string;                    // イベント名
  event_description?: string;            // イベント説明
  
  // アクター情報
  actor: {
    user_id?: string;                   // ユーザーID
    user_email?: string;                // ユーザーメール
    user_name?: string;                 // ユーザー名
    user_role?: string;                 // ユーザーロール
    service_account?: string;           // サービスアカウント
    api_key_id?: string;                // APIキーID
    system?: boolean;                   // システム操作フラグ
  };
  
  // テナント情報
  tenant_id: string;                    // テナントID
  tenant_name?: string;                 // テナント名
  
  // リソース情報
  resource?: {
    type: ResourceType;                 // リソースタイプ
    id: string;                        // リソースID
    name?: string;                     // リソース名
    path?: string;                     // リソースパス
    previous_value?: any;              // 変更前の値
    new_value?: any;                   // 変更後の値
  };
  
  // コンテキスト情報
  context: AuditContext;                // 実行コンテキスト
  
  // 結果情報
  result: {
    status: AuditStatus;               // 結果ステータス
    error_code?: string;               // エラーコード
    error_message?: string;            // エラーメッセージ
    duration_ms?: number;              // 処理時間（ミリ秒）
  };
  
  // セキュリティ情報
  security?: {
    risk_level?: RiskLevel;           // リスクレベル
    compliance_tags?: string[];        // コンプライアンスタグ
    sensitive_data?: boolean;          // 機密データフラグ
    encryption_status?: string;        // 暗号化ステータス
  };
  
  // メタデータ
  metadata?: Record<string, any>;       // カスタムメタデータ
}

// イベントタイプ
type AuditEventType = 
  | "create"               // 作成
  | "read"                 // 読み取り
  | "update"               // 更新
  | "delete"               // 削除
  | "login"                // ログイン
  | "logout"               // ログアウト
  | "export"               // エクスポート
  | "import"               // インポート
  | "execute"              // 実行
  | "approve"              // 承認
  | "reject"               // 却下
  | "share"                // 共有
  | "revoke"               // 取り消し
  | "configure"            // 設定変更
  | "authenticate"         // 認証
  | "authorize"            // 認可
  | "error"                // エラー
  | "warning";             // 警告

// イベントカテゴリ
type AuditEventCategory = 
  | "authentication"       // 認証
  | "authorization"        // 認可
  | "data_access"          // データアクセス
  | "data_modification"    // データ変更
  | "configuration"        // 設定
  | "system"               // システム
  | "security"             // セキュリティ
  | "compliance"           // コンプライアンス
  | "api"                  // API
  | "user_activity";       // ユーザーアクティビティ

// リソースタイプ
type ResourceType = 
  | "user"
  | "chat"
  | "message"
  | "task"
  | "chain"
  | "library"
  | "document"
  | "image"
  | "agent"
  | "plugin"
  | "configuration"
  | "tenant"
  | "api_key"
  | "role"
  | "permission";

// 監査ステータス
type AuditStatus = 
  | "success"              // 成功
  | "failure"              // 失敗
  | "partial"              // 部分的成功
  | "pending"              // 保留中
  | "blocked";             // ブロック

// リスクレベル
type RiskLevel = 
  | "none"
  | "low"
  | "medium"
  | "high"
  | "critical";
```

### AuditEvent

監査イベントの詳細定義：

```typescript
interface AuditEvent {
  // 基本情報
  event_id: string;                      // イベントID
  event_type: AuditEventType;           // イベントタイプ
  event_source: EventSource;            // イベントソース
  
  // タイミング
  initiated_at: string;                  // 開始時刻
  completed_at?: string;                 // 完了時刻
  
  // 詳細データ
  details: {
    action: string;                     // 実行アクション
    parameters?: Record<string, any>;   // パラメータ
    changes?: Array<{                   // 変更内容
      field: string;
      old_value: any;
      new_value: any;
    }>;
    affected_items?: Array<{            // 影響を受けたアイテム
      type: string;
      id: string;
      name?: string;
    }>;
  };
  
  // トレーサビリティ
  correlation_id?: string;              // 相関ID
  parent_event_id?: string;             // 親イベントID
  trace_id?: string;                    // トレースID
}

// イベントソース
type EventSource = 
  | "web_ui"               // Web UI
  | "api"                  // API
  | "cli"                  // CLI
  | "sdk"                  // SDK
  | "webhook"              // Webhook
  | "scheduled_job"        // スケジュールジョブ
  | "system"               // システム
  | "integration";         // 外部連携
```

### AuditContext

監査コンテキスト情報：

```typescript
interface AuditContext {
  // セッション情報
  session?: {
    session_id: string;                 // セッションID
    login_time: string;                 // ログイン時刻
    session_duration_ms?: number;       // セッション継続時間
  };
  
  // ネットワーク情報
  network?: {
    ip_address?: string;                // IPアドレス
    user_agent?: string;                // ユーザーエージェント
    referrer?: string;                  // リファラー
    geo_location?: {                    // 地理的位置
      country?: string;
      region?: string;
      city?: string;
      latitude?: number;
      longitude?: number;
    };
  };
  
  // デバイス情報
  device?: {
    type?: string;                      // デバイスタイプ
    os?: string;                        // OS
    browser?: string;                   // ブラウザ
    device_id?: string;                 // デバイスID
  };
  
  // API情報
  api?: {
    endpoint?: string;                  // APIエンドポイント
    method?: string;                    // HTTPメソッド
    version?: string;                   // APIバージョン
    request_id?: string;                // リクエストID
    response_code?: number;             // レスポンスコード
  };
  
  // 環境情報
  environment?: {
    name?: string;                      // 環境名（production, staging等）
    region?: string;                    // リージョン
    deployment_id?: string;             // デプロイメントID
  };
}
```

## ログカテゴリ型定義

### AccessLog

アクセスログ：

```typescript
interface AccessLog extends AuditLog {
  event_category: "data_access";
  
  access_details: {
    operation: "view" | "download" | "list" | "search";
    resource_count?: number;            // アクセスしたリソース数
    
    // データアクセス詳細
    data_classification?: DataClassification; // データ分類
    access_level?: AccessLevel;         // アクセスレベル
    
    // フィルタ・検索条件
    filters?: Record<string, any>;      // 適用されたフィルタ
    search_query?: string;               // 検索クエリ
    
    // パフォーマンス
    response_time_ms?: number;          // レスポンス時間
    data_size_bytes?: number;           // データサイズ
  };
}

// データ分類
type DataClassification = 
  | "public"
  | "internal"
  | "confidential"
  | "restricted";

// アクセスレベル
type AccessLevel = 
  | "read"
  | "write"
  | "admin"
  | "owner";
```

### OperationLog

操作ログ：

```typescript
interface OperationLog extends AuditLog {
  event_category: "user_activity";
  
  operation_details: {
    operation_type: OperationType;      // 操作タイプ
    target_resource: {                  // 対象リソース
      type: ResourceType;
      id: string;
      name?: string;
    };
    
    // 操作パラメータ
    input_parameters?: Record<string, any>;
    output_result?: any;
    
    // バッチ操作
    batch_operation?: {
      total_items: number;               // 総アイテム数
      processed_items: number;           // 処理済みアイテム数
      failed_items: number;              // 失敗アイテム数
    };
    
    // 承認情報
    approval?: {
      required: boolean;                 // 承認必須フラグ
      approved_by?: string;              // 承認者
      approved_at?: string;              // 承認日時
      approval_comment?: string;         // 承認コメント
    };
  };
}

// 操作タイプ
type OperationType = 
  | "create_resource"
  | "update_resource"
  | "delete_resource"
  | "execute_task"
  | "run_chain"
  | "generate_image"
  | "process_document"
  | "train_model"
  | "deploy_service"
  | "backup_data"
  | "restore_data";
```

### DataChangeLog

データ変更ログ：

```typescript
interface DataChangeLog extends AuditLog {
  event_category: "data_modification";
  
  change_details: {
    change_type: "insert" | "update" | "delete" | "bulk";
    
    // 変更対象
    entity_type: string;                 // エンティティタイプ
    entity_id: string;                   // エンティティID
    entity_version?: number;             // エンティティバージョン
    
    // 変更内容
    changes: Array<{
      field_name: string;                // フィールド名
      field_type: string;                // フィールド型
      old_value: any;                    // 変更前の値
      new_value: any;                    // 変更後の値
      change_reason?: string;            // 変更理由
    }>;
    
    // データ整合性
    validation?: {
      rules_checked: string[];           // チェックされたルール
      validation_passed: boolean;        // バリデーション成功
      validation_errors?: string[];      // バリデーションエラー
    };
    
    // トランザクション
    transaction?: {
      transaction_id: string;            // トランザクションID
      isolation_level?: string;          // 分離レベル
      rollback?: boolean;                // ロールバックフラグ
    };
  };
}
```

### SecurityLog

セキュリティログ：

```typescript
interface SecurityLog extends AuditLog {
  event_category: "security";
  
  security_details: {
    security_event_type: SecurityEventType;
    
    // 脅威情報
    threat?: {
      threat_level: ThreatLevel;        // 脅威レベル
      threat_type?: string;              // 脅威タイプ
      threat_description?: string;       // 脅威の説明
      threat_indicators?: string[];      // 脅威インジケータ
    };
    
    // 認証情報
    authentication?: {
      method: AuthMethod;                // 認証方法
      mfa_used?: boolean;                // MFA使用
      failed_attempts?: number;          // 失敗試行回数
      account_locked?: boolean;          // アカウントロック
    };
    
    // ポリシー違反
    policy_violation?: {
      policy_name: string;               // ポリシー名
      violation_type: string;            // 違反タイプ
      violation_severity: string;        // 違反の重要度
      action_taken?: string;             // 実行されたアクション
    };
    
    // インシデント
    incident?: {
      incident_id?: string;              // インシデントID
      incident_type?: string;            // インシデントタイプ
      response_required?: boolean;       // 対応必要フラグ
    };
  };
}

// セキュリティイベントタイプ
type SecurityEventType = 
  | "login_attempt"
  | "login_success"
  | "login_failure"
  | "logout"
  | "password_change"
  | "permission_change"
  | "access_denied"
  | "suspicious_activity"
  | "data_breach_attempt"
  | "policy_violation"
  | "malware_detected"
  | "ddos_attack";

// 脅威レベル
type ThreatLevel = 
  | "info"
  | "low"
  | "medium"
  | "high"
  | "critical";

// 認証方法
type AuthMethod = 
  | "password"
  | "oauth"
  | "saml"
  | "mfa"
  | "biometric"
  | "certificate"
  | "api_key";
```

## 検索・フィルタ型定義

### AuditLogQuery

監査ログクエリ：

```typescript
interface AuditLogQuery {
  // 時間範囲
  time_range: {
    start_time: string;                  // 開始時刻（ISO 8601）
    end_time: string;                    // 終了時刻（ISO 8601）
  };
  
  // フィルタ条件
  filters?: AuditLogFilter;             // フィルタ
  
  // 検索
  search?: {
    query: string;                      // 検索クエリ
    fields?: string[];                   // 検索対象フィールド
  };
  
  // ソート
  sort?: {
    field: string;                       // ソートフィールド
    order: "asc" | "desc";               // ソート順
  };
  
  // ページネーション
  pagination?: {
    limit: number;                       // 取得件数
    offset?: number;                     // オフセット
    cursor?: string;                     // カーソル
  };
  
  // 集約
  aggregation?: {
    group_by?: string[];                 // グループ化フィールド
    metrics?: AggregationMetric[];      // 集計メトリクス
  };
}

// 集計メトリクス
interface AggregationMetric {
  type: "count" | "sum" | "avg" | "min" | "max";
  field?: string;
  alias?: string;
}
```

### AuditLogFilter

監査ログフィルタ：

```typescript
interface AuditLogFilter {
  // イベントフィルタ
  event_types?: AuditEventType[];       // イベントタイプ
  event_categories?: AuditEventCategory[]; // イベントカテゴリ
  event_names?: string[];                // イベント名
  
  // アクターフィルタ
  user_ids?: string[];                  // ユーザーID
  user_emails?: string[];                // ユーザーメール
  user_roles?: string[];                 // ユーザーロール
  service_accounts?: string[];          // サービスアカウント
  
  // テナントフィルタ
  tenant_ids?: string[];                 // テナントID
  
  // リソースフィルタ
  resource_types?: ResourceType[];      // リソースタイプ
  resource_ids?: string[];               // リソースID
  
  // 結果フィルタ
  statuses?: AuditStatus[];             // ステータス
  has_error?: boolean;                  // エラー有無
  
  // セキュリティフィルタ
  risk_levels?: RiskLevel[];            // リスクレベル
  compliance_tags?: string[];           // コンプライアンスタグ
  sensitive_data?: boolean;             // 機密データフラグ
  
  // ネットワークフィルタ
  ip_addresses?: string[];              // IPアドレス
  countries?: string[];                 // 国
  
  // カスタムフィルタ
  custom_filters?: Array<{
    field: string;
    operator: FilterOperator;
    value: any;
  }>;
}

// フィルタ演算子
type FilterOperator = 
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
  | "regex";               // 正規表現
```

## 集計・分析型定義

### AuditStatistics

監査統計：

```typescript
interface AuditStatistics {
  // 期間
  period: {
    start_time: string;
    end_time: string;
  };
  
  // 基本統計
  total_events: number;                  // 総イベント数
  unique_users: number;                  // ユニークユーザー数
  unique_resources: number;              // ユニークリソース数
  
  // イベント別統計
  events_by_type: Record<AuditEventType, number>;
  events_by_category: Record<AuditEventCategory, number>;
  events_by_status: Record<AuditStatus, number>;
  
  // 時系列統計
  time_series?: Array<{
    timestamp: string;
    count: number;
    type?: string;
  }>;
  
  // ユーザー別統計
  top_users?: Array<{
    user_id: string;
    user_email?: string;
    event_count: number;
  }>;
  
  // リソース別統計
  top_resources?: Array<{
    resource_type: ResourceType;
    resource_id: string;
    access_count: number;
  }>;
  
  // セキュリティ統計
  security_stats?: {
    failed_logins: number;
    security_incidents: number;
    policy_violations: number;
    high_risk_events: number;
  };
  
  // パフォーマンス統計
  performance_stats?: {
    avg_response_time_ms: number;
    max_response_time_ms: number;
    min_response_time_ms: number;
    p95_response_time_ms: number;
    p99_response_time_ms: number;
  };
}
```

### AuditReport

監査レポート：

```typescript
interface AuditReport {
  // レポート情報
  report_id: string;                    // レポートID
  report_type: ReportType;              // レポートタイプ
  report_name: string;                  // レポート名
  
  // 生成情報
  generated_at: string;                  // 生成日時
  generated_by: string;                  // 生成者
  
  // レポート期間
  period: {
    start_time: string;
    end_time: string;
  };
  
  // レポート内容
  summary: {
    total_events: number;
    total_users: number;
    compliance_score?: number;           // コンプライアンススコア
    risk_assessment?: string;            // リスク評価
  };
  
  // 詳細セクション
  sections: Array<{
    title: string;
    type: "text" | "table" | "chart";
    content: any;
  }>;
  
  // 推奨事項
  recommendations?: Array<{
    severity: "low" | "medium" | "high";
    category: string;
    description: string;
    action_items?: string[];
  }>;
  
  // エクスポート情報
  export_format?: "pdf" | "csv" | "json" | "html";
  export_url?: string;
}

// レポートタイプ
type ReportType = 
  | "compliance"           // コンプライアンス
  | "security"             // セキュリティ
  | "user_activity"        // ユーザーアクティビティ
  | "data_access"          // データアクセス
  | "system_usage"         // システム使用状況
  | "incident"             // インシデント
  | "custom";              // カスタム
```

## API リクエスト/レスポンス型定義

### ログ記録

```typescript
// ログ記録リクエスト
interface RecordAuditLogRequest {
  event_type: AuditEventType;           // イベントタイプ（必須）
  event_name: string;                   // イベント名（必須）
  event_description?: string;           // イベント説明
  
  resource?: {
    type: ResourceType;
    id: string;
    name?: string;
  };
  
  result: {
    status: AuditStatus;
    error_code?: string;
    error_message?: string;
  };
  
  metadata?: Record<string, any>;       // カスタムメタデータ
}

// ログ記録レスポンス
interface RecordAuditLogResponse {
  log_id: string;                       // 記録されたログID
  timestamp: string;                    // タイムスタンプ
}
```

### ログ検索

```typescript
// ログ検索リクエスト
interface SearchAuditLogsRequest {
  query: AuditLogQuery;                 // 検索クエリ（必須）
  include_details?: boolean;            // 詳細情報を含める
}

// ログ検索レスポンス
interface SearchAuditLogsResponse {
  logs: AuditLog[];                     // ログ配列
  total: number;                        // 総件数
  
  pagination?: {
    has_more: boolean;                  // 追加データ有無
    next_cursor?: string;                // 次のカーソル
  };
  
  aggregations?: Record<string, any>;   // 集計結果
}
```

### ログエクスポート

```typescript
// ログエクスポートリクエスト
interface ExportAuditLogsRequest {
  query: AuditLogQuery;                 // エクスポート対象クエリ（必須）
  
  format: "csv" | "json" | "parquet";   // エクスポート形式（必須）
  
  options?: {
    include_headers?: boolean;          // ヘッダーを含める（CSV）
    compression?: "gzip" | "zip";       // 圧縮形式
    encryption?: boolean;                // 暗号化
    max_records?: number;                // 最大レコード数
  };
  
  delivery?: {
    method: "download" | "email" | "s3" | "webhook";
    destination?: string;                // 配信先
  };
}

// ログエクスポートレスポンス
interface ExportAuditLogsResponse {
  export_id: string;                    // エクスポートID
  status: "pending" | "processing" | "completed" | "failed";
  
  // 完了時
  download_url?: string;                // ダウンロードURL
  expires_at?: string;                  // 有効期限
  
  // 統計
  record_count?: number;                // レコード数
  file_size_bytes?: number;             // ファイルサイズ
}
```

### コンプライアンスレポート

```typescript
// コンプライアンスレポート生成リクエスト
interface GenerateComplianceReportRequest {
  report_type: "gdpr" | "hipaa" | "sox" | "pci_dss" | "custom";
  
  period: {
    start_date: string;                  // 開始日
    end_date: string;                    // 終了日
  };
  
  scope?: {
    tenant_ids?: string[];               // 対象テナント
    user_ids?: string[];                 // 対象ユーザー
    resource_types?: ResourceType[];    // 対象リソース
  };
  
  include_sections?: string[];          // 含めるセクション
  format: "pdf" | "html" | "json";      // 出力形式
}

// コンプライアンスレポート生成レスポンス
interface GenerateComplianceReportResponse {
  report: AuditReport;                  // レポート
  compliance_status: {
    compliant: boolean;                 // 準拠状態
    violations?: Array<{                // 違反事項
      rule: string;
      severity: string;
      description: string;
      occurrences: number;
    }>;
    score?: number;                      // コンプライアンススコア
  };
}
```

## 保持ポリシー型定義

```typescript
// ログ保持ポリシー
interface AuditLogRetentionPolicy {
  policy_id: string;                    // ポリシーID
  policy_name: string;                  // ポリシー名
  
  // 保持期間
  retention_period: {
    value: number;                      // 期間値
    unit: "days" | "months" | "years";  // 単位
  };
  
  // 適用条件
  conditions?: {
    event_categories?: AuditEventCategory[];
    resource_types?: ResourceType[];
    risk_levels?: RiskLevel[];
    compliance_tags?: string[];
  };
  
  // アーカイブ設定
  archive?: {
    enabled: boolean;                   // アーカイブ有効化
    destination: "s3" | "glacier" | "azure_archive" | "gcp_coldline";
    after_days: number;                 // アーカイブまでの日数
  };
  
  // 削除設定
  deletion?: {
    enabled: boolean;                   // 自動削除有効化
    after_days: number;                 // 削除までの日数
    require_approval?: boolean;         // 承認必須
  };
  
  // 法的保持
  legal_hold?: {
    enabled: boolean;                   // 法的保持有効化
    reason?: string;                     // 理由
    expires_at?: string;                // 有効期限
  };
}

// 保持ポリシー更新リクエスト
interface UpdateRetentionPolicyRequest {
  policy_id: string;
  retention_period?: {
    value: number;
    unit: "days" | "months" | "years";
  };
  archive?: {
    enabled: boolean;
    after_days?: number;
  };
  deletion?: {
    enabled: boolean;
    after_days?: number;
  };
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - 監査ログ基本型定義
  - ログカテゴリ型定義（アクセス、操作、データ変更、セキュリティ）
  - 検索・フィルタ型定義
  - 集計・分析型定義
  - API リクエスト/レスポンス型定義
  - 保持ポリシー型定義