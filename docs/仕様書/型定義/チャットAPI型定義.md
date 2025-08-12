# チャットAPI型定義

## 目次

1. [概要](#概要)
2. [チャット管理API](#チャット管理api)
   - [チャット一覧取得](#チャット一覧取得)
     - [GetChatsParams](#getchatsparams)
     - [GetChatsResponse](#getchatsresponse)
     - [ChatRoom](#chatroom)
   - [チャット作成・メッセージ追加](#チャット作成メッセージ追加)
     - [CreateChatRequest](#createchatrequest)
     - [CreateChatResponse](#createchatresponse)
     - [ChatMode](#chatmode)
   - [チャットストリーミング](#チャットストリーミング)
     - [ChatStreamRequest](#chatstreamrequest)
     - [TextChunkEvent](#textchunkevent)
     - [ImageGeneratingEvent](#imagegeneratingevent)
     - [ImageGeneratedEvent](#imagegeneratedevent)
     - [StreamErrorEvent](#streamerrorevent)
     - [StreamCompleteEvent](#streamcompleteevent)
3. [メッセージ型定義](#メッセージ型定義)
   - [ChatMessage](#chatmessage)
   - [MessageRole](#messagerole)
   - [RAGContext](#ragcontext)
   - [FileAttachment](#fileattachment)
   - [AgentInfo](#agentinfo)
4. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのチャット機能で使用される型定義。リアルタイムチャット、ストリーミング応答、メッセージ管理に関する型を定義する。

本ドキュメントは[チャット仕様書](../チャット仕様書.md)に基づいて作成されており、実装時の型定義リファレンスとして使用する。

## チャット管理API

### チャット一覧取得

#### GetChatsParams
```typescript
interface GetChatsParams {
  page?: number;                   // ページ番号（デフォルト: 1）
  limit?: number;                  // 取得件数（デフォルト: 20、最大: 100）
  sort?: "created_at" | "updated_at";  // ソート項目（デフォルト: "updated_at"）
  order?: "asc" | "desc";          // ソート順（デフォルト: "desc"）
}
```

#### GetChatsResponse
```typescript
interface GetChatsResponse {
  chats: ChatRoom[];               // チャット一覧
  total: number;                   // 総件数
  page: number;                    // 現在のページ番号
  limit: number;                   // 取得件数
  total_pages: number;             // 総ページ数
}
```

#### ChatRoom
```typescript
interface ChatRoom {
  // 識別子
  room_id: string;                 // チャットルームID
  user_id: string;                 // 所有者ID
  
  // 基本情報
  title: string;                   // ルームタイトル
  created_at: string;              // 作成日時（ISO 8601）
  updated_at: string;              // 最終更新日時
  
  // 統計情報
  message_count: number;           // メッセージ数
  last_message?: {                 // 最後のメッセージ（オプション）
    content: string;               // 最後のメッセージ（プレビュー）
    timestamp: string;             // タイムスタンプ
    role: string;                  // 発言者役割
  };
  
  // 設定
  settings?: {                     // チャット設定（オプション）
    system_prompt?: string;        // カスタムプロンプト
    temperature?: number;          // LLM温度設定
    active_modes?: string[];       // 有効なモード
  };
}
```

### チャット作成・メッセージ追加

#### CreateChatRequest
```typescript
interface CreateChatRequest {
  chat_id?: UUID;                  // 既存チャットID（既存チャットに追加する場合）
  message: string;                 // メッセージ内容
  active_modes?: ChatMode[];       // アクティブモード（オプション）
}
```

#### CreateChatResponse
```typescript
interface CreateChatResponse {
  chat_id: UUID;                   // チャットID
  message_id: UUID;                // メッセージID
  title?: string;                  // チャットタイトル（新規作成時のみ）
  created_at: DateTime;            // 作成日時
}
```

#### ChatMode
```typescript
type ChatMode = "chat" | "image" | "web" | "rag";
```

### チャットストリーミング

Server-Sent Events（SSE）を使用したストリーミング応答の型定義。

#### StreamMessage
```typescript
// ストリーミング用の簡略版メッセージ
interface StreamMessage {
  role: MessageRole;               // 送信者の役割
  content: string;                 // メッセージ内容
  timestamp?: string;              // タイムスタンプ（オプション）
}
```

#### ChatStreamRequest
```typescript
interface ChatStreamRequest {
  messages: StreamMessage[];       // 簡略版メッセージ履歴（必須）
  chat_id?: string;                // 既存チャットID（オプション）
  modes?: ChatMode[];              // アクティブモード（オプション）
  stream: true;                    // ストリーミングフラグ（必須）
  temperature?: number;            // 生成温度（0.0-1.0、オプション）
  max_tokens?: number;             // 最大トークン数（オプション）
  search_keywords?: string[];      // エージェント検索キーワード（オプション）
}
```

#### ストリーミングレスポンス（Server-Sent Events）

##### TextChunkEvent
```typescript
// テキストチャンク
interface TextChunkEvent {
  type: 'text';                    // イベントタイプ
  content: string;                 // テキストコンテンツの断片
}
```

##### ImageGeneratingEvent
```typescript
// 画像生成開始
interface ImageGeneratingEvent {
  type: 'generating_image';        // イベントタイプ
  generating_image: true;          // 画像生成中フラグ
}
```

##### ImageGeneratedEvent
```typescript
// 画像生成完了
interface ImageGeneratedEvent {
  type: 'images';                  // イベントタイプ
  images: Array<{                  // 生成された画像の配列
    url: string;                   // 画像URL
    prompt: string;                // 生成プロンプト
  }>;
}
```

##### StreamErrorEvent
```typescript
// エラー
interface StreamErrorEvent {
  type: 'error';                   // イベントタイプ
  error: string;                   // エラーメッセージ
}
```

##### StreamCompleteEvent
```typescript
// 完了
interface StreamCompleteEvent {
  type: 'done';                    // イベントタイプ
  done: true;                      // 完了フラグ
  chat_id: string;                 // チャットID
  message_id: string;              // 生成されたメッセージID
}
```


## メッセージ型定義

### ChatMessage
```typescript
interface ChatMessage {
  // 識別子
  message_id: string;              // メッセージID
  user_id: string;                 // ユーザーID
  room_id: string;                 // チャットルームID
  
  // タイムスタンプ
  timestamp: string;               // ISO 8601形式（UTC）
  
  // メッセージ情報
  role: MessageRole;               // 送信者の役割
  content: string;                 // メッセージ本文
  
  // RAGコンテキスト（非表示）
  context?: RAGContext;            // RAGコンテキスト（オプション）
  
  // 添付ファイル
  attachments?: FileAttachment[];  // 添付ファイル（オプション）
  
  // エージェント実行情報（assistantロールの場合）
  agent_info?: AgentInfo;          // エージェント情報（オプション）
}
```

### MessageRole
```typescript
type MessageRole = 'user' | 'assistant' | 'system';
```

### RAGContext
```typescript
interface RAGContext {
  rag_sources: Array<{             // RAGソース情報
    title: string;                 // ソースタイトル
    source: string;                // ソース種別（internal-db, web等）
    content: string;               // 参照されたテキスト
    score: number;                 // 関連性スコア（0.0-1.0）
  }>;
}
```

### FileAttachment
```typescript
interface FileAttachment {
  type: 'image' | 'pdf' | 'document' | 'audio' | 'video'; // ファイルタイプ
  url: string;                     // ファイルURL（署名付き）
  thumbnail?: string;              // サムネイルURL（画像の場合）
  name?: string;                   // ファイル名
  size?: number;                   // ファイルサイズ（バイト）
}
```

### AgentInfo
```typescript
interface AgentInfo {
  mode: 'chat' | 'web' | 'image' | 'rag'; // エージェントモード
  execution_time_ms: number;       // 実行時間（ミリ秒）
  tokens_used?: number;            // 使用トークン数（オプション）
}
```

## WebSocket通信型定義

### WebSocketメッセージ送信
```typescript
interface WebSocketMessageRequest {
  action: "chat";                  // アクション種別
  data: {
    content: string;               // メッセージ内容
    chat_id: string;               // チャットID
    modes: ChatMode[];             // アクティブモード
  };
}
```

### WebSocketメッセージ受信
```typescript
interface WebSocketMessageResponse {
  action: "message";               // アクション種別
  data: {
    type: "text" | "error" | "complete";  // メッセージタイプ
    content?: string;              // テキスト内容（typeがtextの場合）
    error?: string;                // エラーメッセージ（typeがerrorの場合）
    message_id?: string;           // 生成されたメッセージID（typeがcompleteの場合）
  };
}
```

## エラーレスポンス型定義

### ErrorResponse
```typescript
interface ErrorResponse {
  error: {
    code: string;                  // エラーコード
    message: string;               // エラーメッセージ
    details?: any;                 // 詳細情報（オプション）
  };
  status: number;                  // HTTPステータスコード
  timestamp: string;               // タイムスタンプ（ISO 8601）
}
```

### ErrorCode
```typescript
enum ErrorCode {
  // 認証関連
  AUTH_INVALID_TOKEN = 'AUTH001',
  AUTH_TOKEN_EXPIRED = 'AUTH002',
  AUTH_INSUFFICIENT_PERMISSIONS = 'AUTH003',
  
  // チャット関連
  CHAT_NOT_FOUND = 'CHAT001',
  CHAT_ACCESS_DENIED = 'CHAT002',
  CHAT_LIMIT_EXCEEDED = 'CHAT003',
  
  // メッセージ関連
  MESSAGE_INVALID_FORMAT = 'MSG001',
  MESSAGE_RATE_LIMIT = 'MSG002',
  
  // システム関連
  INTERNAL_SERVER_ERROR = 'SYS001',
  SERVICE_UNAVAILABLE = 'SYS002',
  TIMEOUT = 'SYS003'
}
```

## 更新履歴

- 2025-08-05: 初版作成（チャット管理API、画像生成API、エージェントAPI、メッセージ型定義）
- 2025-08-05: チャット仕様書に合わせて大幅更新（ChatMessage、ChatRoom型定義を追加、ストリーミングイベントにtypeフィールドを追加、画像生成APIとエージェントAPIを別ファイルに分割予定のため削除）
- 2025-08-06: チャット仕様書の更新に合わせて以下を追加・修正
  - ChatStreamRequestを仕様書の形式に合わせて修正（messagesフィールド追加、streamフラグ必須化）
  - WebSocket通信の型定義を追加
  - エラーレスポンスの型定義を追加