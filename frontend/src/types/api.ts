/**
 * API型定義
 * 
 * このファイルはドキュメント（/makoto/docs/仕様書/型定義/）に
 * 完全準拠した型定義です。
 * 
 * 変更する場合は必ずドキュメントを先に更新してください。
 */

// ============================================
// 基本型
// ============================================

export type UUID = string;
export type DateTime = string; // ISO 8601形式

// ============================================
// チャットAPI型定義
// ドキュメント: /makoto/docs/仕様書/型定義/チャットAPI型定義.md
// ============================================

/**
 * メッセージロール
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * チャットモード
 */
export type ChatMode = 'chat' | 'image' | 'web' | 'rag';

/**
 * チャットルーム
 */
export interface ChatRoom {
  // 識別子
  room_id: string;  // ドキュメント準拠
  user_id: string;
  
  // 基本情報
  title: string;
  created_at: DateTime;
  updated_at: DateTime;
  
  // 統計情報
  message_count: number;
  last_message?: {
    content: string;
    timestamp: DateTime;
    role: string;
  };
  
  // 設定
  settings?: {
    system_prompt?: string;
    temperature?: number;
    active_modes?: string[];
  };
}

/**
 * チャットメッセージ
 */
export interface ChatMessage {
  // 識別子
  message_id: string;
  user_id: string;
  room_id: string;
  
  // タイムスタンプ
  timestamp: DateTime;
  
  // メッセージ情報
  role: MessageRole;
  content: string;
  
  // RAGコンテキスト（非表示）
  context?: RAGContext;
  
  // 添付ファイル
  attachments?: FileAttachment[];
  
  // エージェント実行情報（assistantロールの場合）
  agent_info?: AgentInfo;
}

/**
 * RAGコンテキスト
 */
export interface RAGContext {
  rag_sources: Array<{
    title: string;
    source: string;
    content: string;
    score: number;
  }>;
}

/**
 * ファイル添付
 */
export interface FileAttachment {
  type: 'image' | 'pdf' | 'document' | 'audio' | 'video';
  url: string;
  thumbnail?: string;
  name?: string;
  size?: number;
}

/**
 * エージェント情報
 */
export interface AgentInfo {
  mode: ChatMode;
  execution_time_ms: number;
  tokens_used?: number;
}

/**
 * チャット一覧取得パラメータ
 */
export interface GetChatsParams {
  page?: number;
  limit?: number;
  sort?: 'created_at' | 'updated_at';
  order?: 'asc' | 'desc';
}

/**
 * チャット一覧レスポンス
 */
export interface GetChatsResponse {
  chats: ChatRoom[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  has_more: boolean;  // ページング用に追加
}

/**
 * チャット作成リクエスト
 */
export interface CreateChatRequest {
  chat_id?: UUID;
  message: string;
  active_modes?: ChatMode[];
}

/**
 * チャット作成レスポンス
 */
export interface CreateChatResponse {
  chat_id: UUID;
  message_id: UUID;
  title?: string;
  created_at: DateTime;
}

/**
 * ストリーミング用の簡略版メッセージ
 */
export interface StreamMessage {
  role: MessageRole;
  content: string;
  timestamp?: string;
}

/**
 * チャットストリーミングリクエスト
 */
export interface ChatStreamRequest {
  messages: StreamMessage[];
  chat_id?: string;
  modes?: ChatMode[];
  stream: true;
  temperature?: number;
  max_tokens?: number;
  search_keywords?: string[];
}

// ============================================
// SSE（Server-Sent Events）型定義
// ドキュメント: /makoto/docs/仕様書/型定義/SSE API型定義.md
// ============================================

/**
 * テキストチャンクイベント
 */
export interface TextChunkEvent {
  type: 'text';
  content: string;
}

/**
 * 画像生成開始イベント
 */
export interface ImageGeneratingEvent {
  type: 'generating_image';
  generating_image: true;
}

/**
 * 画像生成完了イベント
 */
export interface ImageGeneratedEvent {
  type: 'images';
  images: Array<{
    url: string;
    prompt: string;
  }>;
}

/**
 * ストリームエラーイベント
 */
export interface StreamErrorEvent {
  type: 'error';
  error: string;
}

/**
 * ストリーム完了イベント
 */
export interface StreamCompleteEvent {
  type: 'done';
  done: true;
  chat_id: string;
  message_id: string;
}

// ============================================
// エージェントAPI型定義
// ドキュメント: /makoto/docs/仕様書/型定義/エージェントAPI型定義.md
// ============================================

/**
 * エージェントステータスメッセージ
 */
export interface AgentStatusMessage {
  type: 'agent_status';
  content: {
    execution_id: string;
    agent_type: string;
    status: string;
    current_step?: number;
    total_steps?: number;
    message?: string;
  };
}

/**
 * モード分析
 */
export interface ModeAnalysis {
  type: string;
  confidence: number;
  reason: string;
  search_keywords?: string[];
}

/**
 * 分析コンテキスト
 */
export interface AnalyzeContext {
  type: string;
  content: string;
  metadata?: Record<string, string>;
}

/**
 * 分析リクエスト
 */
export interface AnalyzeRequest {
  prompt: string;
  context?: AnalyzeContext[];
}

/**
 * 分析レスポンス
 */
export interface AnalyzeResponse {
  modes: ModeAnalysis[];
  analysis: string;
  primary_mode?: string;
}

/**
 * エージェント思考状態
 */
export type AgentThinkingStatus = 'thinking' | 'analyzing' | 'searching' | 'crawling' | 'generating' | 'complete';

// ============================================
// ライブラリ管理API型定義
// ドキュメント: /makoto/docs/仕様書/型定義/ライブラリ管理API型定義.md
// ============================================

/**
 * ライブラリステータス
 */
export type LibraryStatus = 'active' | 'processing' | 'archived';

/**
 * 公開範囲タイプ
 */
export type VisibilityType = 'private' | 'team' | 'public';

/**
 * ライブラリ公開範囲
 */
export interface LibraryVisibility {
  type: VisibilityType;
  allowed_users?: string[];
  allowed_teams?: string[];
}

/**
 * ライブラリ
 */
export interface Library {
  library_id: UUID;
  name: string;
  description?: string;
  created_by: UUID;
  created_at: DateTime;
  updated_at: DateTime;
  file_count: number;
  total_size: number;
  vectorized_count: number;
  visibility: LibraryVisibility;
  status: LibraryStatus;
  last_vectorized_at?: DateTime;
}

/**
 * ライブラリ一覧取得パラメータ
 */
export interface GetLibrariesParams {
  page?: number;
  limit?: number;
  sort?: 'created_at' | 'updated_at' | 'name';
  order?: 'asc' | 'desc';
  filter?: {
    status?: LibraryStatus;
    visibility_type?: VisibilityType;
  };
}

/**
 * ライブラリ一覧レスポンス
 */
export interface GetLibrariesResponse {
  libraries: Library[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ============================================
// タスク管理API型定義
// ドキュメント: /makoto/docs/仕様書/型定義/タスク管理API型定義.md
// ============================================

/**
 * タスクカテゴリー
 */
export type TaskCategory = 
  | 'text_generation'
  | 'image_generation'
  | 'data_analysis'
  | 'summarization'
  | 'translation'
  | 'code_generation'
  | 'creative_writing'
  | 'business'
  | 'other';

/**
 * タスク実行モード
 */
export type ExecutionMode = 'chat' | 'image' | 'agent' | 'hybrid';

/**
 * タスクステータス
 */
export type TaskStatus = 'draft' | 'active' | 'deprecated' | 'archived';

/**
 * タスク
 */
export interface Task {
  task_id: string;
  name: string;
  description?: string;
  category: TaskCategory;
  tags: string[];
  icon?: string;
  prompt_template: string;
  system_prompt?: string;
  execution_mode: ExecutionMode;
  model_settings?: ModelSettings;
  parameters: TaskParameter[];
  created_by: string;
  created_at: string;
  updated_at: string;
  version: number;
  is_latest: boolean;
  previous_version_id?: string;
  visibility: TaskVisibility;
  status: TaskStatus;
  execution_count: number;
  last_executed_at?: string;
  average_rating?: number;
}

/**
 * モデル設定
 */
export interface ModelSettings {
  model?: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  image_size?: '1024x1024' | '1792x1024' | '1024x1792';
  image_quality?: 'standard' | 'hd';
  image_style?: 'vivid' | 'natural';
  image_count?: number;
  timeout?: number;
  retry_count?: number;
}

/**
 * パラメータバリデーション
 */
export interface ParameterValidation {
  min?: number;
  max?: number;
  pattern?: string;
  options?: string[];
  required?: boolean;
}

/**
 * タスクパラメータ
 */
export interface TaskParameter {
  parameter_id: string;
  name: string;
  label: string;
  description?: string;
  type: 'text' | 'number' | 'select' | 'date' | 'boolean' | 'file' | 'json';
  required: boolean;
  default_value?: string | number | boolean | string[] | Record<string, string>;
  validation?: ParameterValidation;
  ui_type: string;
  placeholder?: string;
  help_text?: string;
  display_order: number;
}

/**
 * タスク公開範囲
 */
export interface TaskVisibility {
  type: 'private' | 'team' | 'public';
  allowed_users?: string[];
  allowed_teams?: string[];
}

// ============================================
// 画像生成API型定義
// ドキュメント: /makoto/docs/仕様書/型定義/画像生成API型定義.md
// ============================================

/**
 * 画像サイズ
 */
export type ImageSize = '1024x1024' | '1792x1024' | '1024x1792';

/**
 * 画像品質
 */
export type ImageQuality = 'standard' | 'hd';

/**
 * 画像スタイル
 */
export type ImageStyle = 'vivid' | 'natural';

/**
 * 画像生成リクエスト
 */
export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  size?: ImageSize;
  quality?: ImageQuality;
  style?: ImageStyle;
  n?: number;
  chat_id?: string;
  user_tags?: string[];
  description?: string;
  async?: boolean;
  webhook_url?: string;
}

/**
 * 画像生成レスポンス
 */
export interface ImageGenerationResponse {
  images?: GeneratedImageData[];
  job_id?: string;
  status?: ImageGenerationStatus;
  request_id: string;
  created_at: string;
  cost?: {
    credits_used: number;
    price_usd: number;
  };
}

/**
 * 生成された画像データ
 */
export interface GeneratedImageData {
  image_id: string;
  url: string;
  thumbnail_url?: string;
  revised_prompt: string;
  metadata: {
    width: number;
    height: number;
    format: string;
    size_bytes: number;
  };
}

/**
 * 画像生成ステータス
 */
export type ImageGenerationStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

// ============================================
// WebクロールAPI型定義
// ドキュメント: /makoto/docs/仕様書/型定義/WebクロールAPI型定義.md
// ============================================

/**
 * クロールジョブタイプ
 */
export type CrawlJobType = 
  | 'single_page'
  | 'site_crawl'
  | 'search_based'
  | 'api_crawl'
  | 'scheduled'
  | 'continuous';

/**
 * クロールジョブステータス
 */
export type CrawlJobStatus = 
  | 'draft'
  | 'ready'
  | 'running'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'cancelled';

/**
 * Webクロールリクエスト
 */
export interface WebCrawlRequest {
  url: string;
  max_depth?: number;
  max_pages?: number;
  wait_time?: number;
  extract_images?: boolean;
  extract_links?: boolean;
}

/**
 * クロール結果
 */
export interface CrawlResult {
  url: string;
  title: string;
  content: string;
  images?: string[];
  links?: string[];
}

/**
 * Webクロールレスポンス
 */
export interface WebCrawlResponse {
  job_id: string;
  status: CrawlJobStatus;
  results?: CrawlResult[];
  error?: string;
}