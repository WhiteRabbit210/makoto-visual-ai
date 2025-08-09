# ライブラリ管理API型定義

## 目次

1. [概要](#概要)
2. [ライブラリ管理](#ライブラリ管理)
   - [ライブラリ一覧取得](#ライブラリ一覧取得)
     - [GetLibrariesParams](#getlibrariesparams)
     - [GetLibrariesResponse](#getlibrariesresponse)
     - [Library](#library)
     - [LibraryStatus](#librarystatus)
   - [ライブラリ詳細取得](#ライブラリ詳細取得)
     - [LibraryDetail](#librarydetail)
   - [ライブラリ作成](#ライブラリ作成)
     - [CreateLibraryRequest](#createlibraryrequest)
     - [CreateLibraryResponse](#createlibraryresponse)
   - [ライブラリ更新](#ライブラリ更新)
     - [UpdateLibraryRequest](#updatelibraryrequest)
     - [UpdateLibraryResponse](#updatelibraryresponse)
   - [ライブラリ削除](#ライブラリ削除)
     - [DeleteLibraryResponse](#deletelibraryresponse)
3. [公開範囲設定](#公開範囲設定)
   - [LibraryVisibility](#libraryvisibility)
   - [VisibilityType](#visibilitytype)
4. [ファイル管理](#ファイル管理)
   - [ファイル一覧取得](#ファイル一覧取得)
     - [GetFilesParams](#getfilesparams)
     - [GetFilesResponse](#getfilesresponse)
     - [LibraryFile](#libraryfile)
     - [VectorizationStatus](#vectorizationstatus)
     - [FileMetadata](#filemetadata)
   - [ファイルアップロード](#ファイルアップロード)
     - [UploadFileRequest](#uploadfilerequest)
     - [UploadFileResponse](#uploadfileresponse)
   - [ファイル削除](#ファイル削除)
     - [DeleteFileResponse](#deletefileresponse)
5. [ベクトル化管理](#ベクトル化管理)
   - [ベクトル化実行](#ベクトル化実行)
     - [VectorizeRequest](#vectorizerequest)
     - [VectorizeResponse](#vectorizeresponse)
   - [ベクトル化状態取得](#ベクトル化状態取得)
     - [VectorizationStatusResponse](#vectorizationstatusresponse)
6. [RAG検索](#rag検索)
   - [ライブラリ検索](#ライブラリ検索)
     - [LibrarySearchRequest](#librarysearchrequest)
     - [LibrarySearchResponse](#librarysearchresponse)
     - [SearchResult](#searchresult)
     - [ChunkMetadata](#chunkmetadata)
   - [検索オプション](#検索オプション)
     - [SearchOptions](#searchoptions)
7. [エンベディングデータ](#エンベディングデータ)
   - [EmbeddingMetadata](#embeddingmetadata)
   - [ChunkData](#chunkdata)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのRAG（Retrieval-Augmented Generation）用ライブラリ管理システムで使用される型定義。FAISSを使用したベクトル検索に最適化された設計。

## ライブラリ管理

### ライブラリ一覧取得

#### GetLibrariesParams
```typescript
interface GetLibrariesParams {
  page?: number;                   // ページ番号（デフォルト: 1）
  limit?: number;                  // 取得件数（デフォルト: 20、最大: 100）
  sort?: "created_at" | "updated_at" | "name";  // ソート項目
  order?: "asc" | "desc";         // ソート順（デフォルト: "desc"）
  filter?: {
    status?: LibraryStatus;        // ステータスフィルタ
    visibility_type?: VisibilityType;  // 公開範囲フィルタ
  };
}
```

#### GetLibrariesResponse
```typescript
interface GetLibrariesResponse {
  libraries: Library[];            // ライブラリ一覧
  total: number;                   // 総件数
  page: number;                    // 現在のページ番号
  limit: number;                   // 取得件数
  total_pages: number;             // 総ページ数
}
```

#### Library
```typescript
interface Library {
  // 基本情報
  library_id: UUID;                // ライブラリID
  name: string;                    // ライブラリ名
  description?: string;            // 説明（オプション）
  
  // 作成者情報
  created_by: UUID;                // 作成者ユーザーID
  created_at: DateTime;            // 作成日時
  updated_at: DateTime;            // 更新日時
  
  // 統計情報
  file_count: number;              // ファイル数
  total_size: number;              // 総ファイルサイズ（バイト）
  vectorized_count: number;        // ベクトル化完了ファイル数
  
  // 公開範囲
  visibility: LibraryVisibility;   // 公開範囲設定
  
  // ステータス
  status: LibraryStatus;           // ライブラリステータス
  last_vectorized_at?: DateTime;   // 最終ベクトル化日時（オプション）
}
```

#### LibraryStatus
```typescript
type LibraryStatus = 
  | "active"        // アクティブ
  | "processing"    // 処理中
  | "archived";     // アーカイブ済み
```

### ライブラリ詳細取得

#### LibraryDetail
```typescript
interface LibraryDetail extends Library {
  // 追加の詳細情報
  vector_dimension: 3072;          // ベクトル次元数（text-embedding-3-large）
  embedding_model: "text-embedding-3-large";  // 使用モデル
  total_chunks: number;            // 総チャンク数
  index_status: {
    faiss_index_size: number;      // FAISSインデックスサイズ（バイト）
    last_rebuild_at?: DateTime;    // 最終再構築日時
  };
  access_logs?: {                  // アクセスログ（管理者のみ）
    last_accessed_at?: DateTime;
    access_count_30d: number;
  };
}
```

### ライブラリ作成

#### CreateLibraryRequest
```typescript
interface CreateLibraryRequest {
  name: string;                    // ライブラリ名（必須）
  description?: string;            // 説明（オプション）
  visibility?: LibraryVisibility;  // 公開範囲（デフォルト: private）
}
```

#### CreateLibraryResponse
```typescript
interface CreateLibraryResponse {
  library_id: UUID;                // 作成されたライブラリID
  name: string;                    // ライブラリ名
  description?: string;            // 説明
  visibility: LibraryVisibility;   // 公開範囲
  created_at: DateTime;            // 作成日時
}
```

### ライブラリ更新

#### UpdateLibraryRequest
```typescript
interface UpdateLibraryRequest {
  name?: string;                   // ライブラリ名（オプション）
  description?: string;            // 説明（オプション）
  visibility?: LibraryVisibility;  // 公開範囲（オプション）
  status?: LibraryStatus;          // ステータス（オプション）
}
```

#### UpdateLibraryResponse
```typescript
interface UpdateLibraryResponse {
  library_id: UUID;                // ライブラリID
  updated_fields: string[];        // 更新されたフィールド名
  updated_at: DateTime;            // 更新日時
}
```

### ライブラリ削除

#### DeleteLibraryResponse
```typescript
interface DeleteLibraryResponse {
  message: string;                 // 成功メッセージ
  deleted_files: number;           // 削除されたファイル数
  deleted_at: DateTime;            // 削除日時
}
```

## 公開範囲設定

### LibraryVisibility
```typescript
interface LibraryVisibility {
  // 公開タイプ
  visibility_type: VisibilityType;
  
  // 部署指定（AND条件）
  departments?: string[];          // 部署名リスト
  
  // 役職指定（AND条件）
  roles?: string[];                // 役職名リスト
  
  // ユーザー指定（OR条件）
  users?: UUID[];                  // ユーザーIDリスト
}
```

### VisibilityType
```typescript
type VisibilityType = 
  | "private"       // 作成者のみ
  | "specific"      // 特定の条件指定
  | "tenant";       // テナント全体
```

## ファイル管理

### ファイル一覧取得

#### GetFilesParams
```typescript
interface GetFilesParams {
  page?: number;                   // ページ番号（デフォルト: 1）
  limit?: number;                  // 取得件数（デフォルト: 20、最大: 100）
  sort?: "uploaded_at" | "filename" | "size";  // ソート項目
  order?: "asc" | "desc";         // ソート順
  filter?: {
    vectorization_status?: VectorizationStatus;  // ベクトル化状態フィルタ
    mime_type?: string;            // MIMEタイプフィルタ
  };
}
```

#### GetFilesResponse
```typescript
interface GetFilesResponse {
  files: LibraryFile[];            // ファイル一覧
  total: number;                   // 総件数
  page: number;                    // 現在のページ番号
  limit: number;                   // 取得件数
  total_pages: number;             // 総ページ数
}
```

#### LibraryFile
```typescript
interface LibraryFile {
  // 基本情報
  file_id: UUID;                   // ファイルID
  library_id: UUID;                // 所属ライブラリID
  filename: string;                // ファイル名
  original_filename: string;       // アップロード時のファイル名
  
  // ファイル情報
  mime_type: string;               // MIMEタイプ
  size: number;                    // ファイルサイズ（バイト）
  file_hash: string;               // ファイルハッシュ（SHA-256）
  storage_path: string;            // ストレージパス
  
  // アップロード情報
  uploaded_by: UUID;               // アップロードユーザーID
  uploaded_at: DateTime;           // アップロード日時
  
  // ベクトル化情報
  vectorization_status: VectorizationStatus;  // ベクトル化ステータス
  vectorized_at?: DateTime;        // ベクトル化完了日時（オプション）
  vectorization_error?: string;    // ベクトル化エラー情報（オプション）
  chunk_count?: number;            // チャンク数（オプション）
  
  // メタデータ
  metadata?: FileMetadata;         // ファイルメタデータ（オプション）
}
```

#### VectorizationStatus
```typescript
type VectorizationStatus = 
  | "pending"       // ベクトル化待ち
  | "processing"    // ベクトル化処理中
  | "completed"     // ベクトル化完了
  | "failed"        // ベクトル化失敗
  | "skipped";      // ベクトル化スキップ（非対応形式）
```

#### FileMetadata
```typescript
interface FileMetadata {
  title?: string;                  // ドキュメントタイトル
  author?: string;                 // 作成者
  created_date?: DateTime;         // ドキュメント作成日
  page_count?: number;             // ページ数（PDFの場合）
  language?: string;               // 言語コード（例: "ja", "en"）
  extracted_text_length?: number;  // 抽出テキスト長
  custom_metadata?: Record<string, any>;  // カスタムメタデータ
}
```

### ファイルアップロード

#### UploadFileRequest
```typescript
// multipart/form-dataで送信
interface UploadFileRequest {
  file: File;                      // アップロードするファイル
  metadata?: string;               // JSONエンコードされたFileMetadata（オプション）
}
```

#### UploadFileResponse
```typescript
interface UploadFileResponse {
  file_id: UUID;                   // ファイルID
  filename: string;                // ファイル名
  size: number;                    // ファイルサイズ（バイト）
  mime_type: string;               // MIMEタイプ
  uploaded_at: DateTime;           // アップロード日時
  vectorization_status: "pending"; // 初期ステータス
}
```

### ファイル削除

#### DeleteFileResponse
```typescript
interface DeleteFileResponse {
  message: string;                 // 成功メッセージ
  deleted_chunks: number;          // 削除されたチャンク数
  deleted_at: DateTime;            // 削除日時
}
```

## ベクトル化管理

### ベクトル化実行

#### VectorizeRequest
```typescript
interface VectorizeRequest {
  file_ids?: UUID[];               // 特定ファイルのみ（オプション）
  force_rebuild?: boolean;         // 強制再ベクトル化（デフォルト: false）
  chunking_options?: {
    chunk_size?: number;           // チャンクサイズ（デフォルト: 1000）
    overlap?: number;              // オーバーラップ（デフォルト: 200）
    max_chunk_tokens?: number;     // 最大トークン数（デフォルト: 256）
  };
}
```

#### VectorizeResponse
```typescript
interface VectorizeResponse {
  job_id: UUID;                    // ジョブID
  status: "queued";                // 初期ステータス
  queued_files: number;            // キューに入ったファイル数
  estimated_time_seconds?: number; // 推定処理時間（秒）
}
```

### ベクトル化状態取得

#### VectorizationStatusResponse
```typescript
interface VectorizationStatusResponse {
  library_id: UUID;                // ライブラリID
  total_files: number;             // 総ファイル数
  status_breakdown: {
    pending: number;               // 待機中
    processing: number;            // 処理中
    completed: number;             // 完了
    failed: number;                // 失敗
    skipped: number;               // スキップ
  };
  active_jobs: {
    job_id: UUID;
    started_at: DateTime;
    files_processed: number;
    files_total: number;
  }[];
  last_completed_at?: DateTime;    // 最終完了日時
}
```

## RAG検索

### ライブラリ検索

#### LibrarySearchRequest
```typescript
interface LibrarySearchRequest {
  query: string;                   // 検索クエリ（必須）
  library_ids?: UUID[];            // 対象ライブラリID（省略時は全アクセス可能ライブラリ）
  options?: SearchOptions;         // 検索オプション
}
```

#### LibrarySearchResponse
```typescript
interface LibrarySearchResponse {
  results: SearchResult[];         // 検索結果
  total_results: number;           // 総結果数
  search_time_ms: number;          // 検索時間（ミリ秒）
  query_embedding_cached: boolean; // クエリエンベディングがキャッシュされていたか
}
```

#### SearchResult
```typescript
interface SearchResult {
  chunk_id: string;                // チャンクID
  file_id: UUID;                   // ファイルID
  library_id: UUID;                // ライブラリID
  score: number;                   // 類似度スコア（0.0-1.0）
  text: string;                    // チャンクテキスト
  metadata: ChunkMetadata;         // チャンクメタデータ
  file_info: {
    filename: string;              // ファイル名
    mime_type: string;             // MIMEタイプ
  };
  library_info: {
    name: string;                  // ライブラリ名
  };
}
```

#### ChunkMetadata
```typescript
interface ChunkMetadata {
  chunk_index: number;             // チャンクインデックス
  start_char: number;              // 開始文字位置
  end_char: number;                // 終了文字位置
  page_number?: number;            // ページ番号（PDFの場合）
  section_title?: string;          // セクション名（オプション）
  token_count: number;             // トークン数
}
```

### 検索オプション

#### SearchOptions
```typescript
interface SearchOptions {
  top_k?: number;                  // 取得件数（デフォルト: 10）
  threshold?: number;              // 類似度閾値（デフォルト: 0.7）
  include_metadata?: boolean;      // メタデータ含有（デフォルト: true）
  rerank?: boolean;                // 再ランキング実施（デフォルト: false）
  search_mode?: "hybrid" | "vector" | "keyword";  // 検索モード（デフォルト: "vector"）
}
```

## エンベディングデータ

### EmbeddingMetadata
```typescript
interface EmbeddingMetadata {
  file_id: UUID;                   // ファイルID
  original_filename: string;       // 元のファイル名
  embedding_model: "text-embedding-3-large";  // 使用モデル（固定値）
  dimensions: 3072;                // ベクトル次元数（固定値）
  total_chunks: number;            // 総チャンク数
  total_tokens: number;            // 総トークン数
  embedding_cost: number;          // エンベディングコスト（USD）
  created_at: DateTime;            // 作成日時
  processing_time_ms: number;      // 処理時間（ミリ秒）
}
```

### ChunkData
```typescript
interface ChunkData {
  chunk_id: string;                // チャンクID（UUID形式）
  chunk_index: number;             // チャンクインデックス
  text: string;                    // チャンクテキスト
  embedding: Float32Array;         // 埋め込みベクトル（3072次元）
  token_count: number;             // トークン数
  metadata: ChunkMetadata;         // チャンクメタデータ
}
```

## 更新履歴

- 2025-08-05: 初版作成（FAISSベースのRAG用ライブラリ管理API型定義）