# 画像生成API型定義

## 目次

1. [概要](#概要)
2. [画像生成API](#画像生成api)
   - [ImageGenerationRequest](#imagegenerationrequest)
   - [ImageGenerationResponse](#imagegenerationresponse)
   - [ImageGenerationStatus](#imagegenerationstatus)
3. [画像生成ジョブAPI](#画像生成ジョブapi)
   - [ImageGenerationJob](#imagegenerationjob)
   - [GetImageJobResponse](#getimagejobresponse)
4. [画像管理API](#画像管理api)
   - [GeneratedImage](#generatedimage)
   - [GetImagesParams](#getimagesparams)
   - [GetImagesResponse](#getimagesresponse)
5. [エラーレスポンス](#エラーレスポンス)
6. [Webhook通知](#webhook通知)
7. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIの画像生成機能で使用される型定義。DALL-E 3を使用した高品質な画像生成と管理機能を提供。

## 画像生成API

### ImageGenerationRequest

画像生成リクエストの型定義：

```typescript
interface ImageGenerationRequest {
  // 生成設定
  prompt: string;                   // 画像生成プロンプト（必須、最大4000文字）
  negative_prompt?: string;         // ネガティブプロンプト（除外したい要素）
  
  // 画像設定
  size?: ImageSize;                 // 画像サイズ（デフォルト: "1024x1024"）
  quality?: ImageQuality;           // 画像品質（デフォルト: "standard"）
  style?: ImageStyle;               // 画像スタイル（デフォルト: "vivid"）
  n?: number;                       // 生成枚数（1-10、デフォルト: 1）
  
  // メタデータ
  chat_id?: string;                 // 関連するチャットID
  user_tags?: string[];             // ユーザー定義タグ
  description?: string;             // 画像の説明
  
  // 非同期処理オプション
  async?: boolean;                  // 非同期生成フラグ（デフォルト: false）
  webhook_url?: string;             // 完了通知用WebhookURL
}

// 画像サイズ
type ImageSize = 
  | "1024x1024"    // 正方形（デフォルト）
  | "1792x1024"    // ランドスケープ
  | "1024x1792";   // ポートレート

// 画像品質
type ImageQuality = 
  | "standard"     // 標準品質（高速、デフォルト）
  | "hd";          // HD品質（高品質、2倍のコスト）

// 画像スタイル
type ImageStyle = 
  | "vivid"        // 鮮やか（デフォルト）
  | "natural";     // 自然
```

### ImageGenerationResponse

画像生成レスポンスの型定義：

```typescript
interface ImageGenerationResponse {
  // 同期生成の場合
  images?: GeneratedImageData[];    // 生成された画像データ
  
  // 非同期生成の場合
  job_id?: string;                  // ジョブID
  status?: ImageGenerationStatus;   // ジョブステータス
  
  // 共通情報
  request_id: string;               // リクエストID
  created_at: string;               // 作成日時（ISO 8601）
  cost?: {                          // コスト情報
    credits_used: number;           // 使用クレジット数
    price_usd: number;              // USD価格
  };
}

interface GeneratedImageData {
  image_id: string;                 // 画像ID
  url: string;                      // 画像URL（署名付き、24時間有効）
  thumbnail_url?: string;           // サムネイルURL
  revised_prompt: string;           // 実際に使用されたプロンプト
  metadata: {
    width: number;                  // 画像幅
    height: number;                 // 画像高さ
    format: string;                 // 画像形式（"png", "webp"等）
    size_bytes: number;             // ファイルサイズ
  };
}
```

### ImageGenerationStatus

画像生成ジョブのステータス：

```typescript
type ImageGenerationStatus = 
  | "pending"       // 待機中
  | "processing"    // 処理中
  | "completed"     // 完了
  | "failed"        // 失敗
  | "cancelled";    // キャンセル

interface ImageGenerationStatusDetail {
  status: ImageGenerationStatus;
  message?: string;                 // ステータスメッセージ
  progress?: number;                // 進捗（0-100）
  estimated_time?: number;          // 推定残り時間（秒）
  error?: {
    code: string;                   // エラーコード
    message: string;                // エラーメッセージ
    details?: any;                  // 詳細情報
  };
}
```

## 画像生成ジョブAPI

### ImageGenerationJob

画像生成ジョブの型定義：

```typescript
interface ImageGenerationJob {
  // 識別情報
  job_id: string;                   // ジョブID
  user_id: string;                  // ユーザーID
  tenant_id: string;                // テナントID
  
  // リクエスト情報
  request: ImageGenerationRequest;  // 元のリクエスト
  request_id: string;               // リクエストID
  
  // ステータス
  status: ImageGenerationStatusDetail; // ステータス詳細
  
  // タイムスタンプ
  created_at: string;               // 作成日時（ISO 8601）
  started_at?: string;              // 開始日時
  completed_at?: string;            // 完了日時
  
  // 結果
  result?: {
    images: GeneratedImageData[];   // 生成された画像
    cost: {
      credits_used: number;
      price_usd: number;
    };
  };
  
  // メタデータ
  priority?: number;                // 優先度（1-10）
  retry_count?: number;             // リトライ回数
  webhook_delivered?: boolean;      // Webhook配信済みフラグ
}
```

### GetImageJobResponse

画像生成ジョブ取得レスポンス：

```typescript
interface GetImageJobResponse {
  job: ImageGenerationJob;          // ジョブ情報
  can_retry: boolean;               // リトライ可能フラグ
  can_cancel: boolean;              // キャンセル可能フラグ
}
```

## 画像管理API

### GeneratedImage

生成済み画像の型定義：

```typescript
interface GeneratedImage {
  // 識別情報
  image_id: string;                 // 画像ID
  user_id: string;                  // ユーザーID
  tenant_id: string;                // テナントID
  
  // 画像情報
  url: string;                      // 画像URL（署名付き）
  permanent_url?: string;           // 永続URL（保存済みの場合）
  thumbnail_url?: string;           // サムネイルURL
  cdn_url?: string;                 // CDN URL
  
  // プロンプト情報
  original_prompt: string;          // オリジナルプロンプト
  revised_prompt: string;           // 実際に使用されたプロンプト
  negative_prompt?: string;         // ネガティブプロンプト
  
  // メタデータ
  metadata: {
    width: number;                  // 画像幅
    height: number;                 // 画像高さ
    format: string;                 // 画像形式
    size_bytes: number;             // ファイルサイズ
    quality: ImageQuality;          // 画像品質
    style: ImageStyle;              // 画像スタイル
  };
  
  // 関連情報
  chat_id?: string;                 // 関連チャットID
  job_id?: string;                  // 生成ジョブID
  
  // タグ・分類
  user_tags?: string[];             // ユーザー定義タグ
  auto_tags?: string[];             // 自動生成タグ（AI分析）
  categories?: string[];            // カテゴリー
  
  // ステータス
  status: 'temporary' | 'saved' | 'deleted'; // 画像ステータス
  is_favorite?: boolean;            // お気に入りフラグ
  is_public?: boolean;              // 公開フラグ
  
  // タイムスタンプ
  created_at: string;               // 作成日時（ISO 8601）
  saved_at?: string;                // 保存日時
  expires_at?: string;              // 有効期限（一時画像の場合）
  
  // 使用統計
  view_count?: number;              // 閲覧回数
  download_count?: number;          // ダウンロード回数
  share_count?: number;             // 共有回数
}
```

### GetImagesParams

画像一覧取得パラメータ：

```typescript
interface GetImagesParams {
  // ページング
  page?: number;                    // ページ番号（デフォルト: 1）
  limit?: number;                   // 取得件数（デフォルト: 20、最大: 100）
  
  // フィルタリング
  status?: ('temporary' | 'saved')[]; // ステータスフィルター
  chat_id?: string;                 // チャットIDフィルター
  tags?: string[];                  // タグフィルター（OR検索）
  categories?: string[];            // カテゴリーフィルター
  is_favorite?: boolean;            // お気に入りフィルター
  
  // 検索
  search?: string;                  // プロンプト検索
  
  // 日付範囲
  created_from?: string;            // 作成日時（開始）
  created_to?: string;              // 作成日時（終了）
  
  // ソート
  sort?: ImageSortField;            // ソートフィールド
  order?: 'asc' | 'desc';           // ソート順（デフォルト: 'desc'）
}

type ImageSortField = 
  | 'created_at'     // 作成日時
  | 'saved_at'       // 保存日時
  | 'view_count'     // 閲覧回数
  | 'size_bytes';    // ファイルサイズ
```

### GetImagesResponse

画像一覧取得レスポンス：

```typescript
interface GetImagesResponse {
  images: GeneratedImage[];         // 画像一覧
  total: number;                    // 総件数
  page: number;                     // 現在のページ
  limit: number;                    // 取得件数
  total_pages: number;              // 総ページ数
  
  // 集計情報
  summary?: {
    total_images: number;           // 総画像数
    saved_images: number;           // 保存済み画像数
    temporary_images: number;       // 一時画像数
    total_size_bytes: number;       // 総ファイルサイズ
    favorite_count: number;         // お気に入り数
  };
}
```

## エラーレスポンス

画像生成特有のエラーレスポンス：

```typescript
interface ImageGenerationError {
  error: {
    code: ImageErrorCode;           // エラーコード
    message: string;                // エラーメッセージ
    details?: {
      prompt_issues?: string[];     // プロンプトの問題点
      safety_issues?: string[];     // 安全性の問題
      remaining_credits?: number;   // 残りクレジット数
      retry_after?: number;         // リトライ可能時間（秒）
    };
  };
  status: number;                   // HTTPステータスコード
  request_id: string;               // リクエストID
}

enum ImageErrorCode {
  // プロンプト関連
  INVALID_PROMPT = 'IMG001',
  PROMPT_TOO_LONG = 'IMG002',
  UNSAFE_PROMPT = 'IMG003',
  
  // リソース関連
  INSUFFICIENT_CREDITS = 'IMG101',
  RATE_LIMIT_EXCEEDED = 'IMG102',
  STORAGE_LIMIT_EXCEEDED = 'IMG103',
  
  // 生成エラー
  GENERATION_FAILED = 'IMG201',
  TIMEOUT = 'IMG202',
  SERVICE_UNAVAILABLE = 'IMG203',
  
  // その他
  INVALID_IMAGE_SIZE = 'IMG301',
  INVALID_PARAMETERS = 'IMG302'
}
```

## Webhook通知

非同期画像生成完了時のWebhook通知形式：

```typescript
interface ImageGenerationWebhook {
  event: 'image.generation.completed' | 'image.generation.failed';
  timestamp: string;                // イベント発生時刻（ISO 8601）
  
  data: {
    job_id: string;                 // ジョブID
    request_id: string;             // リクエストID
    user_id: string;                // ユーザーID
    tenant_id: string;              // テナントID
    
    // 成功時
    images?: GeneratedImageData[];  // 生成された画像
    
    // 失敗時
    error?: {
      code: string;
      message: string;
      details?: any;
    };
  };
  
  // Webhook署名検証用
  signature: string;                // HMAC-SHA256署名
}
```

## 更新履歴

- 2025-08-06: 初版作成
  - DALL-E 3 APIに基づく画像生成型定義
  - 非同期ジョブ管理機能を追加
  - 画像管理・検索機能の型定義を追加
  - Webhook通知形式を定義