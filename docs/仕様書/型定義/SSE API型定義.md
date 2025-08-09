# SSE API型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [SSEMessage](#ssemessage)
   - [SSEMessageType](#ssemessagetype)
   - [SSEMetadata](#ssemetadata)
3. [チャットストリーミング型定義](#チャットストリーミング型定義)
   - [ChatStreamRequest](#chatstreamrequest)
   - [ChatStreamMessage](#chatstreammessage)
   - [ChatCompletionMessage](#chatcompletionmessage)
4. [エージェント実行型定義](#エージェント実行型定義)
   - [AgentStreamRequest](#agentstreamrequest)
   - [AgentStreamMessage](#agentstreammessage)
   - [AgentThinkingMessage](#agentthinkingmessage)
5. [ライブラリ処理型定義](#ライブラリ処理型定義)
   - [LibraryProcessingRequest](#libraryprocessingrequest)
   - [LibraryStreamMessage](#librarystreammessage)
   - [EmbeddingProgressMessage](#embeddingprogressmessage)
6. [エラー型定義](#エラー型定義)
   - [SSEErrorMessage](#sseerrormessage)
   - [SSEErrorCode](#sseerrorcode)
7. [クライアント型定義](#クライアント型定義)
   - [SSEClientConfig](#sseclientconfig)
   - [SSEEventHandlers](#sseeventhandlers)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのSSE（Server-Sent Events）で使用される型定義。チャットストリーミング、エージェント実行、ライブラリ処理など、すべてのリアルタイム通信の型を定義。

本ドキュメントは[SSE仕様書](../SSE仕様書.md)に基づいて作成されており、App Runnerベースの実装を前提としています。

## 基本型定義

### SSEMessage

SSEメッセージの基本構造：

```typescript
interface SSEMessage<T = any> {
  type: SSEMessageType;         // メッセージタイプ
  content?: T;                   // メッセージ内容（型パラメータで指定可能）
  metadata?: SSEMetadata;        // メタデータ
}
```

### SSEMessageType

メッセージタイプの列挙：

```typescript
type SSEMessageType = 
  // チャット関連
  | 'token'                     // LLMトークン
  | 'content_block_start'       // コンテンツブロック開始
  | 'content_block_delta'       // コンテンツブロック差分
  | 'content_block_stop'        // コンテンツブロック終了
  | 'message_complete'          // メッセージ完了
  
  // エージェント関連
  | 'agent_status'             // エージェント状態
  | 'agent_thinking'           // エージェント思考プロセス
  | 'execution_started'        // 実行開始
  | 'step_started'            // ステップ開始
  | 'step_completed'          // ステップ完了
  | 'execution_completed'     // 実行完了
  
  // ライブラリ関連
  | 'library_processing'      // ライブラリ処理中
  | 'embedding_progress'      // エンベディング進捗
  | 'index_update'           // インデックス更新
  | 'file_processing'        // ファイル処理
  
  // システム
  | 'heartbeat'              // ハートビート
  | 'error'                  // エラー
  | 'warning'                // 警告
  | 'info'                   // 情報
  | 'done';                  // 完了
```

### SSEMetadata

メタデータの型定義：

```typescript
interface SSEMetadata {
  timestamp: string;            // ISO 8601形式のタイムスタンプ
  sequence?: number;            // シーケンス番号
  total?: number;              // 総数（進捗表示用）
  request_id?: string;         // リクエストID
  execution_id?: string;       // 実行ID
  [key: string]: any;          // その他の任意のメタデータ
}
```

## チャットストリーミング型定義

### ChatStreamRequest

チャットストリーミングリクエスト：

```typescript
interface ChatStreamRequest {
  chat_id?: string;                    // チャットID
  messages: ChatMessage[];             // メッセージ履歴
  stream: true;                        // ストリーミング有効（必須: true）
  
  // モード設定
  active_modes: Array<'chat' | 'web' | 'agent' | 'image'>;
  
  // モデル設定
  model_settings?: {
    model?: string;                    // モデル名
    temperature?: number;              // 温度（0.0-2.0）
    max_tokens?: number;               // 最大トークン数
    top_p?: number;                    // Top-p（0.0-1.0）
    frequency_penalty?: number;        // 頻度ペナルティ
    presence_penalty?: number;         // 存在ペナルティ
  };
  
  // ライブラリ設定
  library_ids?: string[];              // 使用するライブラリID
  
  // テナント情報（サーバー側で自動設定）
  tenant_id?: string;
  user_id?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  attachments?: MessageAttachment[];
  metadata?: Record<string, any>;
}

interface MessageAttachment {
  type: 'file' | 'image' | 'document';
  url?: string;
  name: string;
  size?: number;
  mime_type?: string;
}
```

### ChatStreamMessage

チャットストリーミングメッセージ：

```typescript
// トークンメッセージ
interface TokenMessage extends SSEMessage {
  type: 'token';
  content: string;                     // トークン文字列
  metadata: {
    timestamp: string;
    sequence: number;                  // トークンのシーケンス番号
  };
}

// コンテンツブロック開始
interface ContentBlockStart extends SSEMessage {
  type: 'content_block_start';
  content: {
    block_id: string;                  // ブロックID
    block_type: 'text' | 'code' | 'image';
    language?: string;                 // コードブロックの言語
  };
}

// コンテンツブロック差分
interface ContentBlockDelta extends SSEMessage {
  type: 'content_block_delta';
  content: {
    block_id: string;
    delta: string;                     // 差分テキスト
  };
}

// コンテンツブロック終了
interface ContentBlockStop extends SSEMessage {
  type: 'content_block_stop';
  content: {
    block_id: string;
  };
}
```

### ChatCompletionMessage

チャット完了メッセージ：

```typescript
interface ChatCompletionMessage extends SSEMessage {
  type: 'message_complete';
  content: {
    message_id: string;                // メッセージID
    total_tokens: number;              // 総トークン数
    prompt_tokens?: number;            // プロンプトトークン数
    completion_tokens?: number;        // 完了トークン数
    model: string;                     // 使用モデル
    finish_reason?: 'stop' | 'length' | 'error';
    
    // エージェント実行結果（エージェントモードの場合）
    agent_results?: {
      web_sources?: WebSource[];
      generated_images?: GeneratedImage[];
      analysis?: any;
    };
    
    // 使用時間とコスト
    duration_ms?: number;              // 処理時間（ミリ秒）
    estimated_cost?: number;           // 推定コスト（USD）
  };
  metadata: SSEMetadata;
}

interface WebSource {
  url: string;
  title: string;
  snippet: string;
  relevance_score?: number;
}

interface GeneratedImage {
  url: string;
  prompt: string;
  size: string;
  style?: string;
}
```

## エージェント実行型定義

### AgentStreamRequest

エージェント実行ストリーミングリクエスト：

```typescript
interface AgentStreamRequest {
  prompt: string;                      // ユーザープロンプト
  
  agent_config?: {
    auto_orchestrate?: boolean;        // 自動オーケストレーション（デフォルト: true）
    selected_agents?: string[];        // 使用エージェントの限定
    
    execution_constraints?: {
      max_steps?: number;              // 最大ステップ数
      timeout_seconds?: number;        // タイムアウト（秒）
      parallel_limit?: number;         // 並列実行数上限
    };
    
    thinking_visibility?: 'full' | 'summary' | 'none'; // 思考プロセス表示レベル
  };
  
  context?: ChatMessage[];            // 会話コンテキスト
}
```

### AgentStreamMessage

エージェントストリーミングメッセージ：

```typescript
// 実行開始
interface ExecutionStartedMessage extends SSEMessage {
  type: 'execution_started';
  content: {
    execution_id: string;              // 実行ID
    total_steps: number;               // 総ステップ数
    plan_summary: string;              // 実行計画の要約
    estimated_time_seconds?: number;   // 推定実行時間
  };
}

// ステップ開始
interface StepStartedMessage extends SSEMessage {
  type: 'step_started';
  content: {
    step: number;                      // ステップ番号
    agent: string;                     // エージェント名
    purpose: string;                   // ステップの目的
    depends_on?: number[];             // 依存ステップ
  };
}

// ステップ完了
interface StepCompletedMessage extends SSEMessage {
  type: 'step_completed';
  content: {
    step: number;
    agent: string;
    success: boolean;
    result?: any;                      // ステップの結果
    error?: {
      code: string;
      message: string;
    };
    duration_ms: number;               // 実行時間
  };
}

// 実行完了
interface ExecutionCompletedMessage extends SSEMessage {
  type: 'execution_completed';
  content: {
    execution_id: string;
    success: boolean;
    total_time_ms: number;
    steps_completed: number;
    steps_failed: number;
    final_result?: any;
  };
}
```

### AgentThinkingMessage

エージェント思考プロセスメッセージ：

```typescript
interface AgentThinkingMessage extends SSEMessage {
  type: 'agent_thinking';
  content: {
    agent_type: string;                // エージェントタイプ
    phase: ThinkingPhase;              // 思考フェーズ
    
    thoughts?: {
      current_analysis?: string;       // 現在の分析
      considered_options?: string[];   // 検討中の選択肢
      selected_approach?: string;      // 選択したアプローチ
      reasoning?: string;              // 推論
      confidence?: number;             // 確信度（0-1）
    };
    
    visibility: 'full' | 'summary' | 'none'; // 表示レベル
  };
  metadata: SSEMetadata & {
    execution_id: string;
    parent_step?: number;
  };
}

type ThinkingPhase = 
  | 'initializing'       // 初期化中
  | 'analyzing'          // 分析中
  | 'planning'           // 計画中
  | 'selecting_agent'    // エージェント選択中
  | 'optimizing'         // 最適化中
  | 'executing'          // 実行中
  | 'evaluating'         // 評価中
  | 'adjusting';         // 調整中
```

## ライブラリ処理型定義

### LibraryProcessingRequest

ライブラリ処理リクエスト：

```typescript
interface LibraryProcessingRequest {
  library_id: string;                  // ライブラリID
  
  action: 'upload' | 'reindex' | 'update' | 'delete';
  
  files?: File[];                      // アップロードファイル（action: 'upload'の場合）
  
  options?: {
    chunk_size?: number;               // チャンクサイズ
    overlap?: number;                  // オーバーラップ
    embedding_model?: string;          // エンベディングモデル
    batch_size?: number;               // バッチサイズ
  };
}
```

### LibraryStreamMessage

ライブラリ処理ストリーミングメッセージ：

```typescript
// ライブラリ処理状態
interface LibraryProcessingMessage extends SSEMessage {
  type: 'library_processing';
  content: {
    library_id: string;
    file?: string;                     // 処理中のファイル名
    status: 'processing' | 'completed' | 'failed';
    
    progress?: {
      current: number;                 // 現在の処理数
      total: number;                   // 総数
      percentage: number;              // パーセンテージ
    };
    
    message?: string;                  // 状態メッセージ
    chunks_processed?: number;         // 処理済みチャンク数
  };
}

// ファイル処理
interface FileProcessingMessage extends SSEMessage {
  type: 'file_processing';
  content: {
    library_id: string;
    file_name: string;
    file_size: number;
    status: 'uploading' | 'extracting' | 'chunking' | 'completed';
    
    progress?: {
      bytes_processed?: number;
      percentage: number;
    };
    
    result?: {
      chunks_created: number;
      text_length: number;
    };
  };
}
```

### EmbeddingProgressMessage

エンベディング進捗メッセージ：

```typescript
interface EmbeddingProgressMessage extends SSEMessage {
  type: 'embedding_progress';
  content: {
    library_id: string;
    file: string;
    
    progress: {
      current: number;                 // 現在のチャンク
      total: number;                   // 総チャンク数
      percentage: number;              // パーセンテージ
    };
    
    embedding_stats?: {
      dimensions: number;              // エンベディング次元数
      model: string;                   // 使用モデル
      tokens_processed: number;        // 処理済みトークン数
    };
  };
}

// インデックス更新
interface IndexUpdateMessage extends SSEMessage {
  type: 'index_update';
  content: {
    library_id: string;
    status: 'updating' | 'completed' | 'failed';
    
    vectors_added?: number;            // 追加されたベクトル数
    total_vectors?: number;            // 総ベクトル数
    index_size_mb?: number;            // インデックスサイズ（MB）
    
    error?: {
      code: string;
      message: string;
    };
  };
}
```

## エラー型定義

### SSEErrorMessage

SSEエラーメッセージ：

```typescript
interface SSEErrorMessage extends SSEMessage {
  type: 'error';
  content: {
    code: SSEErrorCode | string;      // エラーコード
    message: string;                   // エラーメッセージ
    details?: any;                     // 詳細情報
    recoverable: boolean;              // 回復可能かどうか
    retry_after?: number;              // 再試行までの秒数
    
    // エラー発生箇所
    source?: {
      service?: string;                // サービス名
      function?: string;               // 関数名
      line?: number;                  // 行番号
    };
  };
  metadata: SSEMetadata & {
    request_id?: string;
    trace_id?: string;
  };
}
```

### SSEErrorCode

エラーコード定義：

```typescript
enum SSEErrorCode {
  // 接続エラー
  CONNECTION_FAILED = 'SSE001',
  AUTHENTICATION_FAILED = 'SSE002',
  UNAUTHORIZED = 'SSE003',
  
  // ストリーミングエラー
  STREAM_INITIALIZATION_FAILED = 'SSE101',
  STREAM_INTERRUPTED = 'SSE102',
  STREAM_TIMEOUT = 'SSE103',
  
  // レート制限
  RATE_LIMIT_EXCEEDED = 'SSE201',
  QUOTA_EXCEEDED = 'SSE202',
  MESSAGE_SIZE_EXCEEDED = 'SSE203',
  
  // データエラー
  INVALID_REQUEST = 'SSE301',
  INVALID_MESSAGE_FORMAT = 'SSE302',
  MISSING_REQUIRED_FIELD = 'SSE303',
  
  // サーバーエラー
  INTERNAL_SERVER_ERROR = 'SSE500',
  SERVICE_UNAVAILABLE = 'SSE503',
  GATEWAY_TIMEOUT = 'SSE504'
}
```

## クライアント型定義

### SSEClientConfig

SSEクライアント設定：

```typescript
interface SSEClientConfig {
  baseUrl?: string;                    // ベースURL
  token?: string;                      // 認証トークン
  
  // 再接続設定
  reconnect?: {
    enabled: boolean;                  // 自動再接続有効化
    maxAttempts: number;               // 最大再接続試行回数
    initialDelay: number;              // 初期遅延（ミリ秒）
    maxDelay: number;                  // 最大遅延（ミリ秒）
    backoffMultiplier: number;         // バックオフ乗数
  };
  
  // タイムアウト設定
  timeout?: {
    connection: number;                // 接続タイムアウト（ミリ秒）
    idle: number;                      // アイドルタイムアウト（ミリ秒）
  };
  
  // デバッグ設定
  debug?: boolean;                     // デバッグモード
  logger?: (message: string) => void; // カスタムロガー
}
```

### SSEEventHandlers

イベントハンドラー定義：

```typescript
interface SSEEventHandlers {
  // 接続イベント
  onConnected?: () => void;
  onDisconnected?: () => void;
  onReconnecting?: (attempt: number) => void;
  onConnectionLost?: () => void;
  
  // メッセージハンドラー
  onMessage?: (message: SSEMessage) => void;
  onToken?: (token: string) => void;
  onComplete?: (data: any) => void;
  
  // エージェントハンドラー
  onAgentStatus?: (status: any) => void;
  onAgentThinking?: (thoughts: any) => void;
  onStepCompleted?: (step: any) => void;
  
  // ライブラリハンドラー
  onLibraryProgress?: (progress: any) => void;
  onEmbeddingProgress?: (progress: any) => void;
  onIndexUpdate?: (update: any) => void;
  
  // エラーハンドラー
  onError?: (error: SSEErrorMessage) => void;
  onWarning?: (warning: any) => void;
  
  // ハートビート
  onHeartbeat?: () => void;
}
```

## クライアント実装例

```typescript
class SSEClient {
  private eventSource: EventSource | null = null;
  private config: SSEClientConfig;
  private handlers: SSEEventHandlers;
  
  constructor(config: SSEClientConfig, handlers: SSEEventHandlers) {
    this.config = {
      baseUrl: config.baseUrl || this.getDefaultBaseUrl(),
      reconnect: {
        enabled: true,
        maxAttempts: 5,
        initialDelay: 1000,
        maxDelay: 30000,
        backoffMultiplier: 2,
        ...config.reconnect
      },
      ...config
    };
    this.handlers = handlers;
  }
  
  private getDefaultBaseUrl(): string {
    if (process.env.NODE_ENV === 'production') {
      return 'https://makoto-api.awsapprunner.com';
    }
    return 'http://localhost:8000';
  }
  
  async connect(endpoint: string, data?: any): Promise<void> {
    // POSTリクエストでストリーミング開始
    const response = await fetch(`${this.config.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.config.token}`
      },
      body: data ? JSON.stringify(data) : undefined
    });
    
    if (!response.ok) {
      throw new Error(`SSE connection failed: ${response.statusText}`);
    }
    
    // SSE接続確立
    const url = new URL(endpoint, this.config.baseUrl);
    url.searchParams.append('token', this.config.token!);
    
    this.eventSource = new EventSource(url.toString());
    this.setupEventHandlers();
  }
  
  private setupEventHandlers(): void {
    if (!this.eventSource) return;
    
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close();
        this.handlers.onComplete?.(null);
        return;
      }
      
      try {
        const message: SSEMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (e) {
        if (this.config.debug) {
          console.error('Failed to parse SSE message:', e);
        }
      }
    };
    
    this.eventSource.onerror = (error) => {
      if (this.config.debug) {
        console.error('SSE error:', error);
      }
      
      if (this.eventSource?.readyState === EventSource.CLOSED) {
        this.handleReconnect();
      }
    };
    
    this.eventSource.onopen = () => {
      if (this.config.debug) {
        console.log('SSE connection established');
      }
      this.handlers.onConnected?.();
    };
  }
  
  private handleMessage(message: SSEMessage): void {
    // 汎用ハンドラー
    this.handlers.onMessage?.(message);
    
    // タイプ別ハンドラー
    switch (message.type) {
      case 'token':
        this.handlers.onToken?.(message.content as string);
        break;
        
      case 'agent_status':
        this.handlers.onAgentStatus?.(message.content);
        break;
        
      case 'agent_thinking':
        this.handlers.onAgentThinking?.(message.content);
        break;
        
      case 'embedding_progress':
        this.handlers.onEmbeddingProgress?.(message.content);
        break;
        
      case 'error':
        this.handlers.onError?.(message as SSEErrorMessage);
        break;
        
      case 'heartbeat':
        this.handlers.onHeartbeat?.();
        break;
        
      default:
        if (this.config.debug) {
          console.log('Unhandled message type:', message.type);
        }
    }
  }
  
  private handleReconnect(): void {
    // 再接続ロジック実装
    // 省略
  }
  
  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.handlers.onDisconnected?.();
    }
  }
}

// 使用例
const sseClient = new SSEClient(
  {
    baseUrl: 'https://makoto-api.awsapprunner.com',
    token: 'jwt_token_here',
    debug: true
  },
  {
    onToken: (token) => {
      console.log('Received token:', token);
    },
    onAgentThinking: (thoughts) => {
      console.log('Agent thinking:', thoughts);
    },
    onError: (error) => {
      console.error('SSE error:', error);
    }
  }
);

// チャットストリーミング
await sseClient.connect('/api/chat/stream', {
  messages: [{ role: 'user', content: 'Hello' }],
  stream: true
});
```

## 更新履歴

- 2025-08-06: 初版作成
  - SSE基本型定義
  - チャットストリーミング型定義
  - エージェント実行型定義
  - ライブラリ処理型定義
  - クライアント実装例