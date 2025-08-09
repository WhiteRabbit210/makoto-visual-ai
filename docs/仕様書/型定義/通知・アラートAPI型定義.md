# 通知・アラートAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [Notification](#notification)
   - [Alert](#alert)
   - [NotificationChannel](#notificationchannel)
   - [NotificationTemplate](#notificationtemplate)
3. [チャンネル別型定義](#チャンネル別型定義)
   - [SSENotification](#ssenotification)
   - [EmailNotification](#emailnotification)
   - [PushNotification](#pushnotification)
   - [SlackNotification](#slacknotification)
4. [配信設定型定義](#配信設定型定義)
   - [DeliveryConfig](#deliveryconfig)
   - [SubscriptionConfig](#subscriptionconfig)
   - [NotificationPreference](#notificationpreference)
5. [アラート管理型定義](#アラート管理型定義)
   - [AlertRule](#alertrule)
   - [AlertCondition](#alertcondition)
   - [AlertAction](#alertaction)
6. [API リクエスト/レスポンス型定義](#api-リクエストレスポンス型定義)
   - [通知送信](#通知送信)
   - [通知履歴](#通知履歴)
   - [購読管理](#購読管理)
   - [アラート設定](#アラート設定)
7. [リアルタイム通知（SSE）型定義](#リアルタイム通知sse型定義)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの通知・アラート機能で使用される型定義。リアルタイム通知、メール、プッシュ通知、アラート機能などの通知システムに関する構造を定義する。

## 基本型定義

### Notification

通知の基本構造：

```typescript
interface Notification {
  // 識別情報
  notification_id: string;                 // 通知ID（UUID）
  tenant_id: string;                      // テナントID
  
  // 通知タイプと内容
  type: NotificationType;                  // 通知タイプ
  category: NotificationCategory;          // 通知カテゴリ
  priority: NotificationPriority;          // 優先度
  
  // 送信者と受信者
  sender: {
    type: "system" | "user" | "agent";    // 送信者タイプ
    id?: string;                           // 送信者ID
    name?: string;                         // 送信者名
  };
  
  recipients: NotificationRecipient[];     // 受信者リスト
  
  // 通知内容
  content: {
    title: string;                        // タイトル（最大100文字）
    body: string;                         // 本文（最大1000文字）
    summary?: string;                      // 要約（最大200文字）
    html_body?: string;                    // HTML本文（メール用）
    data?: Record<string, any>;           // 追加データ
    attachments?: NotificationAttachment[]; // 添付ファイル
  };
  
  // 配信設定
  channels: NotificationChannel[];         // 配信チャンネル
  delivery_config?: DeliveryConfig;        // 配信設定
  
  // アクション
  actions?: NotificationAction[];          // 通知アクション
  
  // タイミング
  created_at: string;                     // 作成日時（ISO 8601）
  scheduled_at?: string;                  // 予定送信日時
  expires_at?: string;                    // 有効期限
  
  // ステータス
  status: NotificationStatus;              // 通知ステータス
  delivery_status: DeliveryStatus[];       // 配信ステータス（チャンネル別）
  
  // メタデータ
  metadata?: {
    tags?: string[];                      // タグ
    reference_id?: string;                // 参照ID（チャット、タスク等）
    reference_type?: string;              // 参照タイプ
    correlation_id?: string;              // 相関ID
    campaign_id?: string;                 // キャンペーンID
  };
}

// 通知タイプ
type NotificationType = 
  | "info"                  // 情報
  | "success"               // 成功
  | "warning"               // 警告
  | "error"                 // エラー
  | "alert"                 // アラート
  | "announcement"          // お知らせ
  | "reminder"              // リマインダー
  | "invitation"            // 招待
  | "mention"               // メンション
  | "task"                  // タスク
  | "update";               // 更新

// 通知カテゴリ
type NotificationCategory = 
  | "system"                // システム
  | "chat"                  // チャット
  | "task"                  // タスク
  | "collaboration"         // コラボレーション
  | "security"              // セキュリティ
  | "billing"               // 請求
  | "maintenance"           // メンテナンス
  | "marketing";            // マーケティング

// 優先度
type NotificationPriority = 
  | "low"                   // 低
  | "normal"                // 通常
  | "high"                  // 高
  | "urgent";               // 緊急

// 通知ステータス
type NotificationStatus = 
  | "draft"                 // 下書き
  | "scheduled"             // 予定
  | "sending"               // 送信中
  | "sent"                  // 送信済み
  | "delivered"             // 配信済み
  | "failed"                // 失敗
  | "cancelled";            // キャンセル
```

### Alert

アラートの基本構造：

```typescript
interface Alert extends Notification {
  // アラート固有のプロパティ
  alert_id: string;                        // アラートID
  severity: AlertSeverity;                 // 重要度
  
  // アラート発生源
  source: {
    type: AlertSourceType;                 // ソースタイプ
    service?: string;                      // サービス名
    component?: string;                    // コンポーネント名
    metric?: string;                       // メトリクス名
    threshold?: number;                    // 閾値
    current_value?: number;                // 現在値
  };
  
  // アラート状態
  alert_state: AlertState;                 // アラート状態
  acknowledged?: boolean;                  // 確認済みフラグ
  acknowledged_by?: string;                // 確認者
  acknowledged_at?: string;                // 確認日時
  
  // 解決情報
  resolved?: boolean;                      // 解決済みフラグ
  resolved_by?: string;                   // 解決者
  resolved_at?: string;                   // 解決日時
  resolution_notes?: string;              // 解決メモ
  
  // エスカレーション
  escalation_level?: number;              // エスカレーションレベル
  escalated_to?: string[];                // エスカレート先
  
  // 関連アラート
  parent_alert_id?: string;               // 親アラートID
  related_alert_ids?: string[];           // 関連アラートID
}

// アラート重要度
type AlertSeverity = 
  | "info"
  | "warning"
  | "minor"
  | "major"
  | "critical";

// アラートソースタイプ
type AlertSourceType = 
  | "metric"                // メトリクス
  | "log"                   // ログ
  | "synthetic"             // 合成監視
  | "user_report"           // ユーザーレポート
  | "system";               // システム

// アラート状態
type AlertState = 
  | "active"                // アクティブ
  | "acknowledged"          // 確認済み
  | "suppressed"            // 抑制中
  | "resolved";             // 解決済み
```

### NotificationChannel

通知チャンネルの定義：

```typescript
interface NotificationChannel {
  channel_id?: string;                     // チャンネルID
  type: ChannelType;                       // チャンネルタイプ
  enabled: boolean;                        // 有効/無効
  
  // チャンネル設定
  config?: {
    // SSE設定
    sse?: {
      connection_id?: string;              // 接続ID
      topic?: string;                      // トピック
      filter?: Record<string, any>;        // フィルタ条件
    };
    
    // メール設定
    email?: {
      to?: string[];                       // 宛先
      cc?: string[];                       // CC
      bcc?: string[];                      // BCC
      reply_to?: string;                   // 返信先
      template_id?: string;                // テンプレートID
      use_html?: boolean;                  // HTML形式
    };
    
    // プッシュ通知設定
    push?: {
      device_tokens?: string[];            // デバイストークン
      platform?: "ios" | "android" | "web"; // プラットフォーム
      badge?: number;                      // バッジ数
      sound?: string;                      // 通知音
      icon?: string;                       // アイコンURL
      image?: string;                      // 画像URL
    };
    
    // Slack設定
    slack?: {
      webhook_url?: string;                // Webhook URL
      channel?: string;                    // チャンネル名
      username?: string;                   // ユーザー名
      icon_emoji?: string;                 // 絵文字アイコン
      mention?: string[];                  // メンション
    };
    
    // SMS設定
    sms?: {
      phone_numbers?: string[];            // 電話番号
      sender_id?: string;                  // 送信者ID
    };
  };
  
  // 配信オプション
  delivery_options?: {
    retry?: boolean;                       // リトライ有効
    max_retries?: number;                  // 最大リトライ回数
    timeout_seconds?: number;              // タイムアウト（秒）
    rate_limit?: number;                   // レート制限（件/分）
  };
}

// チャンネルタイプ
type ChannelType = 
  | "sse"                   // Server-Sent Events
  | "email"                 // メール
  | "push"                  // プッシュ通知
  | "slack"                 // Slack
  | "teams"                 // Microsoft Teams
  | "sms"                   // SMS
  | "webhook"               // Webhook
  | "in_app";               // アプリ内通知
```

### NotificationTemplate

通知テンプレートの定義：

```typescript
interface NotificationTemplate {
  template_id: string;                     // テンプレートID
  name: string;                            // テンプレート名
  description?: string;                    // 説明
  
  // テンプレートタイプ
  type: NotificationType;                  // 通知タイプ
  category: NotificationCategory;          // カテゴリ
  
  // テンプレート内容
  content: {
    title_template: string;                // タイトルテンプレート
    body_template: string;                 // 本文テンプレート
    html_template?: string;                // HTMLテンプレート
    
    // 変数定義
    variables: TemplateVariable[];         // テンプレート変数
    
    // 多言語対応
    locales?: Record<string, {             // ロケール別テンプレート
      title: string;
      body: string;
      html?: string;
    }>;
  };
  
  // デフォルト設定
  defaults?: {
    channels?: ChannelType[];              // デフォルトチャンネル
    priority?: NotificationPriority;       // デフォルト優先度
    expires_in_hours?: number;             // デフォルト有効期限（時間）
  };
  
  // メタデータ
  created_by: string;                      // 作成者
  created_at: string;                      // 作成日時
  updated_at: string;                      // 更新日時
  is_active: boolean;                      // 有効フラグ
}

// テンプレート変数
interface TemplateVariable {
  name: string;                            // 変数名
  type: "string" | "number" | "boolean" | "date" | "array" | "object";
  required: boolean;                       // 必須フラグ
  default_value?: any;                     // デフォルト値
  description?: string;                    // 説明
  format?: string;                         // フォーマット（日付等）
}
```

## チャンネル別型定義

### SSENotification

SSE（Server-Sent Events）通知：

```typescript
interface SSENotification {
  // SSEイベント
  event_type: string;                      // イベントタイプ
  event_id: string;                        // イベントID
  
  // データペイロード
  data: {
    notification: Notification;             // 通知本体
    timestamp: string;                     // タイムスタンプ
    sequence?: number;                     // シーケンス番号
  };
  
  // 配信情報
  retry?: number;                          // リトライ間隔（ミリ秒）
  target_connections?: string[];           // 対象接続ID
}

// SSE接続管理
interface SSEConnection {
  connection_id: string;                   // 接続ID
  user_id: string;                        // ユーザーID
  tenant_id: string;                      // テナントID
  
  // 接続情報
  established_at: string;                  // 接続確立時刻
  last_event_at?: string;                 // 最終イベント時刻
  last_event_id?: string;                 // 最終イベントID
  
  // 購読設定
  subscriptions: {
    topics: string[];                       // 購読トピック
    filters?: Record<string, any>;         // フィルタ条件
  };
  
  // 接続状態
  status: "connected" | "disconnected" | "reconnecting";
  reconnect_count?: number;                // 再接続回数
  
  // クライアント情報
  client_info?: {
    ip_address?: string;
    user_agent?: string;
    device_id?: string;
  };
}
```

### EmailNotification

メール通知：

```typescript
interface EmailNotification {
  // メール基本情報
  message_id?: string;                     // メッセージID
  
  // 送信者・受信者
  from: {
    email: string;                         // 送信元メールアドレス
    name?: string;                         // 送信者名
  };
  
  to: EmailRecipient[];                    // 宛先
  cc?: EmailRecipient[];                   // CC
  bcc?: EmailRecipient[];                  // BCC
  reply_to?: string;                       // 返信先
  
  // メール内容
  subject: string;                         // 件名
  text_body?: string;                      // テキスト本文
  html_body?: string;                      // HTML本文
  
  // 添付ファイル
  attachments?: EmailAttachment[];         // 添付ファイル
  
  // メールヘッダー
  headers?: Record<string, string>;        // カスタムヘッダー
  
  // 配信設定
  importance?: "low" | "normal" | "high";  // 重要度
  tracking?: {
    open_tracking?: boolean;               // 開封追跡
    click_tracking?: boolean;              // クリック追跡
    unsubscribe_link?: boolean;            // 配信停止リンク
  };
  
  // テンプレート利用
  template?: {
    template_id: string;                   // テンプレートID
    template_data: Record<string, any>;    // テンプレートデータ
  };
}

// メール受信者
interface EmailRecipient {
  email: string;                           // メールアドレス
  name?: string;                          // 名前
  type?: "to" | "cc" | "bcc";             // 受信者タイプ
}

// メール添付ファイル
interface EmailAttachment {
  filename: string;                        // ファイル名
  content: string;                         // 内容（Base64エンコード）
  content_type: string;                   // MIMEタイプ
  content_id?: string;                    // コンテンツID（インライン画像用）
  disposition?: "attachment" | "inline";   // 配置
}
```

### PushNotification

プッシュ通知：

```typescript
interface PushNotification {
  // プッシュ通知基本情報
  notification: {
    title: string;                         // タイトル
    body: string;                          // 本文
    icon?: string;                         // アイコンURL
    image?: string;                        // 画像URL
    badge?: number;                        // バッジ数
    sound?: string;                        // 通知音
    tag?: string;                          // タグ（グループ化用）
    color?: string;                        // 色（Android）
  };
  
  // データペイロード
  data?: Record<string, any>;              // カスタムデータ
  
  // プラットフォーム別設定
  platform_config?: {
    // iOS設定（APNs）
    ios?: {
      badge?: number;                      // バッジ数
      sound?: string;                      // 通知音
      category?: string;                   // カテゴリ
      thread_id?: string;                  // スレッドID
      subtitle?: string;                   // サブタイトル
      mutable_content?: boolean;           // 変更可能コンテンツ
      content_available?: boolean;         // サイレントプッシュ
      interruption_level?: "passive" | "active" | "time-sensitive" | "critical";
    };
    
    // Android設定（FCM）
    android?: {
      channel_id?: string;                 // チャンネルID
      priority?: "normal" | "high";        // 優先度
      ttl?: number;                        // TTL（秒）
      restricted_package_name?: string;    // パッケージ名制限
      notification_priority?: "min" | "low" | "default" | "high" | "max";
      visibility?: "private" | "public" | "secret";
      vibrate_pattern?: number[];          // バイブレーションパターン
      light_settings?: {                   // LEDライト設定
        color: string;
        on_duration_ms: number;
        off_duration_ms: number;
      };
    };
    
    // Web設定（Web Push）
    web?: {
      icon?: string;                       // アイコンURL
      badge?: string;                      // バッジURL
      image?: string;                      // 画像URL
      vibrate?: number[];                  // バイブレーション
      timestamp?: number;                  // タイムスタンプ
      require_interaction?: boolean;       // 操作必須
      actions?: Array<{                    // アクションボタン
        action: string;
        title: string;
        icon?: string;
      }>;
    };
  };
  
  // 配信対象
  targets: {
    device_tokens?: string[];              // デバイストークン
    user_ids?: string[];                   // ユーザーID
    topic?: string;                        // トピック
    condition?: string;                    // 条件式
  };
  
  // 配信オプション
  options?: {
    priority?: "normal" | "high";          // 配信優先度
    time_to_live?: number;                 // 有効期限（秒）
    collapse_key?: string;                 // 折りたたみキー
    dry_run?: boolean;                     // ドライラン
  };
}
```

### SlackNotification

Slack通知：

```typescript
interface SlackNotification {
  // Slack基本設定
  channel?: string;                        // チャンネル（#general等）
  username?: string;                       // Bot名
  icon_emoji?: string;                     // 絵文字アイコン
  icon_url?: string;                       // アイコンURL
  
  // メッセージ内容
  text?: string;                           // メインテキスト
  mrkdwn?: boolean;                        // Markdownサポート
  
  // リッチメッセージ
  blocks?: SlackBlock[];                   // Blockキット
  attachments?: SlackAttachment[];         // 添付（レガシー）
  
  // メンション
  mentions?: {
    users?: string[];                      // ユーザーメンション（@user）
    channels?: string[];                   // チャンネルメンション（@channel）
    here?: boolean;                        // @here
    everyone?: boolean;                    // @everyone
  };
  
  // スレッド
  thread_ts?: string;                      // スレッドタイムスタンプ
  reply_broadcast?: boolean;               // チャンネルにも投稿
}

// Slackブロック
interface SlackBlock {
  type: "section" | "divider" | "image" | "actions" | "context" | "header";
  block_id?: string;
  text?: {
    type: "plain_text" | "mrkdwn";
    text: string;
    emoji?: boolean;
  };
  fields?: Array<{
    type: "plain_text" | "mrkdwn";
    text: string;
  }>;
  accessory?: any;                         // アクセサリ要素
  elements?: any[];                        // 要素配列
}

// Slack添付（レガシー）
interface SlackAttachment {
  color?: string;                          // 色（good, warning, danger, #hex）
  pretext?: string;                        // プレテキスト
  author_name?: string;                    // 著者名
  author_link?: string;                    // 著者リンク
  author_icon?: string;                    // 著者アイコン
  title?: string;                          // タイトル
  title_link?: string;                     // タイトルリンク
  text?: string;                           // テキスト
  fields?: Array<{
    title: string;
    value: string;
    short?: boolean;
  }>;
  image_url?: string;                      // 画像URL
  thumb_url?: string;                      // サムネイルURL
  footer?: string;                         // フッター
  footer_icon?: string;                    // フッターアイコン
  ts?: number;                             // タイムスタンプ
}
```

## 配信設定型定義

### DeliveryConfig

配信設定：

```typescript
interface DeliveryConfig {
  // 配信タイミング
  timing: {
    immediate?: boolean;                    // 即時配信
    scheduled_at?: string;                  // 予定日時
    timezone?: string;                      // タイムゾーン
    
    // 繰り返し設定
    recurring?: {
      enabled: boolean;
      pattern: RecurrencePattern;          // 繰り返しパターン
      interval?: number;                    // 間隔
      count?: number;                       // 回数
      until?: string;                       // 終了日
    };
  };
  
  // バッチ配信
  batching?: {
    enabled: boolean;                      // バッチ配信有効
    batch_size?: number;                   // バッチサイズ
    interval_seconds?: number;             // バッチ間隔（秒）
  };
  
  // 配信条件
  conditions?: {
    user_online?: boolean;                 // ユーザーオンライン時のみ
    business_hours_only?: boolean;         // 営業時間内のみ
    quiet_hours?: {                        // 静音時間
      start: string;                       // 開始時刻（HH:mm）
      end: string;                         // 終了時刻（HH:mm）
    };
  };
  
  // 重複制御
  deduplication?: {
    enabled: boolean;                      // 重複排除有効
    key?: string;                          // 重複判定キー
    window_minutes?: number;               // 重複判定期間（分）
  };
  
  // エラーハンドリング
  error_handling?: {
    retry_policy?: {
      max_attempts: number;                // 最大試行回数
      initial_delay_ms: number;            // 初回遅延（ミリ秒）
      max_delay_ms: number;                // 最大遅延（ミリ秒）
      multiplier: number;                  // バックオフ係数
    };
    fallback_channel?: ChannelType;        // フォールバックチャンネル
  };
}

// 繰り返しパターン
type RecurrencePattern = 
  | "daily"
  | "weekly"
  | "monthly"
  | "yearly"
  | "custom";
```

### SubscriptionConfig

購読設定：

```typescript
interface SubscriptionConfig {
  subscription_id: string;                  // 購読ID
  user_id: string;                         // ユーザーID
  tenant_id: string;                       // テナントID
  
  // 購読対象
  subscriptions: {
    // カテゴリ別購読
    categories?: {
      [key in NotificationCategory]?: boolean;
    };
    
    // タイプ別購読
    types?: {
      [key in NotificationType]?: boolean;
    };
    
    // トピック購読
    topics?: string[];                     // 購読トピック
    
    // 送信者購読
    senders?: string[];                    // 特定送信者の通知
  };
  
  // チャンネル設定
  channel_preferences: {
    [key in ChannelType]?: {
      enabled: boolean;                    // 有効/無効
      config?: any;                        // チャンネル固有設定
    };
  };
  
  // 配信ルール
  delivery_rules?: {
    priority_threshold?: NotificationPriority; // 最低優先度
    aggregate_similar?: boolean;           // 類似通知をまとめる
    max_per_hour?: number;                 // 時間あたり最大数
    max_per_day?: number;                  // 日あたり最大数
  };
  
  // 静音設定
  mute_settings?: {
    all_muted?: boolean;                   // 全通知ミュート
    muted_until?: string;                  // ミュート終了日時
    muted_categories?: NotificationCategory[]; // ミュートカテゴリ
    muted_senders?: string[];              // ミュート送信者
  };
  
  // メタデータ
  created_at: string;                      // 作成日時
  updated_at: string;                      // 更新日時
  is_active: boolean;                      // 有効フラグ
}
```

### NotificationPreference

通知設定：

```typescript
interface NotificationPreference {
  user_id: string;                         // ユーザーID
  tenant_id: string;                       // テナントID
  
  // グローバル設定
  global_settings: {
    enabled: boolean;                      // 通知有効/無効
    language: string;                      // 言語設定
    timezone: string;                      // タイムゾーン
    
    // 営業時間
    business_hours?: {
      enabled: boolean;
      days: number[];                      // 曜日（0=日曜）
      start_time: string;                  // 開始時刻
      end_time: string;                    // 終了時刻
    };
    
    // 静音時間
    quiet_hours?: {
      enabled: boolean;
      start_time: string;                  // 開始時刻
      end_time: string;                    // 終了時刻
    };
  };
  
  // デバイス設定
  devices?: NotificationDevice[];          // デバイスリスト
  
  // 配信先設定
  delivery_endpoints?: {
    email?: string;                        // メールアドレス
    phone?: string;                        // 電話番号
    slack_user_id?: string;                // Slack ユーザーID
    webhook_url?: string;                  // Webhook URL
  };
  
  // カスタム設定
  custom_settings?: Record<string, any>;
}

// 通知デバイス
interface NotificationDevice {
  device_id: string;                       // デバイスID
  platform: "ios" | "android" | "web";     // プラットフォーム
  device_token?: string;                   // デバイストークン
  push_enabled: boolean;                   // プッシュ通知有効
  registered_at: string;                   // 登録日時
  last_used_at?: string;                  // 最終使用日時
}
```

## アラート管理型定義

### AlertRule

アラートルール：

```typescript
interface AlertRule {
  rule_id: string;                         // ルールID
  name: string;                           // ルール名
  description?: string;                    // 説明
  
  // ルール条件
  conditions: AlertCondition[];             // 条件リスト
  condition_logic?: "all" | "any" | "custom"; // 条件ロジック
  custom_expression?: string;              // カスタム条件式
  
  // アラート設定
  alert_config: {
    severity: AlertSeverity;               // 重要度
    type: NotificationType;                // 通知タイプ
    category: NotificationCategory;        // カテゴリ
    
    // 通知内容テンプレート
    template: {
      title: string;                       // タイトルテンプレート
      body: string;                        // 本文テンプレート
      data?: Record<string, any>;          // 追加データ
    };
  };
  
  // アクション
  actions: AlertAction[];                  // アクションリスト
  
  // スケジュール
  schedule?: {
    enabled: boolean;                      // スケジュール有効
    check_interval_seconds?: number;       // チェック間隔（秒）
    active_hours?: {                       // アクティブ時間
      start: string;
      end: string;
    };
  };
  
  // 抑制設定
  suppression?: {
    enabled: boolean;                      // 抑制有効
    duration_minutes?: number;             // 抑制期間（分）
    max_alerts_per_hour?: number;          // 時間あたり最大アラート数
  };
  
  // エスカレーション
  escalation?: {
    enabled: boolean;                      // エスカレーション有効
    levels: Array<{
      level: number;                       // レベル
      after_minutes: number;               // 経過時間（分）
      notify: string[];                    // 通知先
    }>;
  };
  
  // メタデータ
  created_by: string;                      // 作成者
  created_at: string;                      // 作成日時
  updated_at: string;                      // 更新日時
  is_active: boolean;                      // 有効フラグ
  tags?: string[];                         // タグ
}
```

### AlertCondition

アラート条件：

```typescript
interface AlertCondition {
  condition_id: string;                    // 条件ID
  type: ConditionType;                     // 条件タイプ
  
  // メトリクス条件
  metric?: {
    name: string;                          // メトリクス名
    aggregation: "avg" | "sum" | "min" | "max" | "count";
    window_seconds: number;                // ウィンドウ期間（秒）
    operator: ComparisonOperator;          // 比較演算子
    threshold: number;                     // 閾値
    unit?: string;                         // 単位
  };
  
  // ログ条件
  log?: {
    pattern: string;                       // ログパターン
    count_threshold?: number;              // 回数閾値
    window_seconds: number;                // ウィンドウ期間（秒）
  };
  
  // イベント条件
  event?: {
    event_type: string;                    // イベントタイプ
    filters?: Record<string, any>;         // フィルタ条件
    count_threshold?: number;              // 回数閾値
    window_seconds: number;                // ウィンドウ期間（秒）
  };
  
  // カスタム条件
  custom?: {
    expression: string;                    // カスタム式
    language: "javascript" | "python";     // 言語
  };
}

// 条件タイプ
type ConditionType = 
  | "metric"                // メトリクス
  | "log"                   // ログ
  | "event"                 // イベント
  | "custom";               // カスタム

// 比較演算子
type ComparisonOperator = 
  | "eq"                    // 等しい
  | "ne"                    // 等しくない
  | "gt"                    // より大きい
  | "gte"                   // 以上
  | "lt"                    // より小さい
  | "lte";                  // 以下
```

### AlertAction

アラートアクション：

```typescript
interface AlertAction {
  action_id: string;                       // アクションID
  type: ActionType;                        // アクションタイプ
  
  // 通知アクション
  notification?: {
    channels: ChannelType[];               // 通知チャンネル
    recipients: string[];                  // 受信者
    template_id?: string;                  // テンプレートID
  };
  
  // Webhook アクション
  webhook?: {
    url: string;                           // Webhook URL
    method: "GET" | "POST" | "PUT";        // HTTPメソッド
    headers?: Record<string, string>;      // ヘッダー
    body?: any;                            // ボディ
    timeout_seconds?: number;              // タイムアウト（秒）
  };
  
  // スクリプトアクション
  script?: {
    type: "lambda" | "inline";             // スクリプトタイプ
    function_name?: string;                // Lambda関数名
    code?: string;                         // インラインコード
    runtime?: string;                      // ランタイム
  };
  
  // 自動修復アクション
  remediation?: {
    type: "restart" | "scale" | "rollback" | "custom";
    target: string;                        // 対象リソース
    parameters?: Record<string, any>;      // パラメータ
  };
  
  // 実行条件
  conditions?: {
    execute_on?: "alert" | "recovery" | "both"; // 実行タイミング
    delay_seconds?: number;                // 遅延実行（秒）
  };
}

// アクションタイプ
type ActionType = 
  | "notification"          // 通知
  | "webhook"               // Webhook
  | "script"                // スクリプト
  | "remediation"           // 自動修復
  | "ticket"                // チケット作成
  | "escalate";             // エスカレーション
```

## API リクエスト/レスポンス型定義

### 通知送信

```typescript
// 通知送信リクエスト
interface SendNotificationRequest {
  // 通知タイプと内容
  type: NotificationType;                  // 通知タイプ（必須）
  priority?: NotificationPriority;         // 優先度
  
  // 受信者
  recipients: Array<{                      // 受信者リスト（必須）
    user_id?: string;
    email?: string;
    phone?: string;
    device_token?: string;
  }>;
  
  // 通知内容
  content: {                              // 通知内容（必須）
    title: string;
    body: string;
    data?: Record<string, any>;
  };
  
  // チャンネル指定
  channels?: ChannelType[];                // 配信チャンネル
  
  // 配信オプション
  options?: {
    scheduled_at?: string;                  // 予定送信日時
    expires_at?: string;                   // 有効期限
    deduplication_key?: string;            // 重複排除キー
  };
  
  // テンプレート使用
  template?: {
    template_id: string;                   // テンプレートID
    template_data: Record<string, any>;    // テンプレートデータ
  };
}

// 通知送信レスポンス
interface SendNotificationResponse {
  notification_id: string;                  // 通知ID
  status: "queued" | "sending" | "sent";   // ステータス
  
  delivery_status?: Array<{                // チャンネル別配信状態
    channel: ChannelType;
    status: "pending" | "sent" | "failed";
    message_id?: string;
    error?: string;
  }>;
  
  scheduled_at?: string;                   // 予定送信日時
  estimated_delivery?: string;             // 推定配信時刻
}
```

### 通知履歴

```typescript
// 通知履歴取得リクエスト
interface GetNotificationHistoryRequest {
  // フィルタ条件
  user_id?: string;                        // ユーザーID
  type?: NotificationType;                 // 通知タイプ
  category?: NotificationCategory;         // カテゴリ
  status?: NotificationStatus;             // ステータス
  
  // 期間指定
  date_from?: string;                      // 開始日
  date_to?: string;                        // 終了日
  
  // ページネーション
  limit?: number;                           // 取得件数（デフォルト: 20）
  offset?: number;                          // オフセット
  cursor?: string;                         // カーソル
  
  // ソート
  sort_by?: "created_at" | "priority" | "status";
  sort_order?: "asc" | "desc";
}

// 通知履歴取得レスポンス
interface GetNotificationHistoryResponse {
  notifications: Notification[];            // 通知リスト
  total: number;                           // 総件数
  
  pagination?: {
    has_more: boolean;                     // 追加データ有無
    next_cursor?: string;                  // 次のカーソル
  };
  
  summary?: {
    total_sent: number;                    // 送信総数
    total_delivered: number;               // 配信成功数
    total_failed: number;                  // 配信失敗数
    by_type: Record<NotificationType, number>;
  };
}
```

### 購読管理

```typescript
// 購読設定更新リクエスト
interface UpdateSubscriptionRequest {
  user_id: string;                         // ユーザーID（必須）
  
  // 購読設定
  subscriptions?: {
    categories?: Record<NotificationCategory, boolean>;
    types?: Record<NotificationType, boolean>;
    topics?: string[];
  };
  
  // チャンネル設定
  channel_preferences?: {
    [key in ChannelType]?: {
      enabled: boolean;
      config?: any;
    };
  };
  
  // 配信ルール
  delivery_rules?: {
    priority_threshold?: NotificationPriority;
    max_per_hour?: number;
    max_per_day?: number;
  };
  
  // ミュート設定
  mute_settings?: {
    all_muted?: boolean;
    muted_until?: string;
    muted_categories?: NotificationCategory[];
  };
}

// 購読設定取得レスポンス
interface GetSubscriptionResponse {
  subscription: SubscriptionConfig;        // 購読設定
  preferences: NotificationPreference;     // 通知設定
  devices: NotificationDevice[];           // デバイスリスト
}
```

### アラート設定

```typescript
// アラートルール作成リクエスト
interface CreateAlertRuleRequest {
  name: string;                            // ルール名（必須）
  description?: string;                    // 説明
  
  // 条件定義
  conditions: AlertCondition[];            // 条件リスト（必須）
  condition_logic?: "all" | "any";         // 条件ロジック
  
  // アラート設定
  alert_config: {                          // アラート設定（必須）
    severity: AlertSeverity;
    template: {
      title: string;
      body: string;
    };
  };
  
  // アクション
  actions?: AlertAction[];                 // アクションリスト
  
  // スケジュール
  schedule?: {
    check_interval_seconds?: number;
    active_hours?: {
      start: string;
      end: string;
    };
  };
  
  // タグ
  tags?: string[];                         // タグ
}

// アラート発生リクエスト
interface TriggerAlertRequest {
  rule_id?: string;                        // ルールID
  severity: AlertSeverity;                 // 重要度（必須）
  
  // アラート内容
  content: {                              // アラート内容（必須）
    title: string;
    body: string;
    source?: {
      type: AlertSourceType;
      metric?: string;
      current_value?: number;
      threshold?: number;
    };
  };
  
  // 通知設定
  notify?: {
    recipients: string[];                  // 通知先
    channels?: ChannelType[];              // チャンネル
  };
  
  // メタデータ
  metadata?: Record<string, any>;          // メタデータ
}

// アラート確認リクエスト
interface AcknowledgeAlertRequest {
  alert_id: string;                        // アラートID（必須）
  acknowledged_by: string;                 // 確認者（必須）
  notes?: string;                          // メモ
}

// アラート解決リクエスト
interface ResolveAlertRequest {
  alert_id: string;                        // アラートID（必須）
  resolved_by: string;                     // 解決者（必須）
  resolution_notes?: string;               // 解決メモ
  root_cause?: string;                     // 根本原因
}
```

## リアルタイム通知（SSE）型定義

```typescript
// SSE接続確立
interface SSEConnectionRequest {
  // ヘッダー認証
  headers: {
    Authorization: string;                  // Bearer トークン
    "X-Tenant-ID": string;                 // テナントID
  };
  
  // クエリパラメータ
  query?: {
    topics?: string;                       // 購読トピック（カンマ区切り）
    last_event_id?: string;                // 最終イベントID
  };
}

// SSEイベントストリーム
interface SSEEventStream {
  // イベントフォーマット
  event?: string;                          // イベント名
  data: string;                            // JSONデータ（文字列化）
  id?: string;                             // イベントID
  retry?: number;                          // 再接続間隔（ミリ秒）
}

// SSEイベントタイプ
enum SSEEventType {
  // システムイベント
  CONNECTED = "connected",                 // 接続確立
  HEARTBEAT = "heartbeat",                // ハートビート
  RECONNECT = "reconnect",                // 再接続要求
  
  // 通知イベント
  NOTIFICATION = "notification",           // 通知
  ALERT = "alert",                        // アラート
  MESSAGE = "message",                    // メッセージ
  
  // 状態変更イベント
  STATUS_CHANGE = "status_change",        // ステータス変更
  UPDATE = "update",                      // 更新
  DELETE = "delete",                      // 削除
}

// SSEデータペイロード
interface SSEDataPayload {
  type: SSEEventType;                      // イベントタイプ
  timestamp: string;                       // タイムスタンプ
  sequence?: number;                       // シーケンス番号
  
  // ペイロード内容（イベントタイプによって異なる）
  payload: {
    // 通知の場合
    notification?: Notification;
    
    // アラートの場合
    alert?: Alert;
    
    // その他のデータ
    data?: any;
  };
  
  // メタデータ
  metadata?: {
    correlation_id?: string;               // 相関ID
    source?: string;                       // ソース
    version?: string;                      // バージョン
  };
}
```

## 更新履歴

- 2025-08-07: 初版作成
  - 通知・アラート基本型定義
  - チャンネル別型定義（SSE、メール、プッシュ通知、Slack）
  - 配信設定型定義
  - アラート管理型定義
  - API リクエスト/レスポンス型定義
  - リアルタイム通知（SSE）型定義