# ファイル管理API型定義

## 目次
- [概要](#概要)
- [基本型定義](#基本型定義)
  - [File](#file)
  - [FileMetadata](#filemetadata)
  - [FileVersion](#fileversion)
  - [FilePermission](#filepermission)
- [ストレージ管理](#ストレージ管理)
  - [StorageProvider](#storageprovider)
  - [StorageBucket](#storagebucket)
  - [StorageQuota](#storagequota)
- [ファイル操作](#ファイル操作)
  - [FileUploadRequest](#fileuploadrequest)
  - [FileUploadResponse](#fileuploadresponse)
  - [FileDownloadRequest](#filedownloadrequest)
  - [FileDownloadResponse](#filedownloadresponse)
- [ファイル変換](#ファイル変換)
  - [ConversionJob](#conversionjob)
  - [ConversionConfig](#conversionconfig)
  - [ConversionResult](#conversionresult)
- [API定義](#api定義)
  - [レスポンス型](#レスポンス型)
  - [エラー型](#エラー型)

## 概要
MAKOTO Visual AIのファイル管理システムに関する型定義です。S3互換ストレージでのファイル管理、アップロード、ダウンロード、変換処理を含みます。

## 基本型定義

### File
```typescript
// ファイル基本情報
interface File {
  // ファイルID
  file_id: string;
  
  // ファイル名
  filename: string;
  
  // オリジナルファイル名
  original_filename: string;
  
  // ファイルパス（S3キー）
  file_path: string;
  
  // バケット名
  bucket: string;
  
  // MIMEタイプ
  mime_type: string;
  
  // ファイルサイズ（バイト）
  file_size: number;
  
  // ファイルハッシュ（SHA-256）
  file_hash: string;
  
  // メタデータ
  metadata: FileMetadata;
  
  // アップロード者
  uploaded_by: string;
  
  // アップロード日時
  uploaded_at: string;
  
  // 最終更新日時
  updated_at: string;
  
  // ファイル状態
  status: 'uploading' | 'processing' | 'ready' | 'error' | 'deleted';
  
  // 公開設定
  visibility: 'private' | 'public' | 'shared';
  
  // タグ
  tags?: string[];
  
  // カスタム属性
  custom_attributes?: Record<string, any>;
}
```

### FileMetadata
```typescript
// ファイルメタデータ
interface FileMetadata {
  // 画像メタデータ
  image?: {
    width: number;
    height: number;
    format: string;
    color_space?: string;
    has_transparency?: boolean;
    dpi?: number;
    exif?: Record<string, any>;
  };
  
  // 動画メタデータ
  video?: {
    width: number;
    height: number;
    duration: number;
    format: string;
    codec: string;
    framerate: number;
    bitrate?: number;
    has_audio?: boolean;
  };
  
  // 音声メタデータ
  audio?: {
    duration: number;
    format: string;
    codec: string;
    sample_rate: number;
    channels: number;
    bitrate?: number;
  };
  
  // ドキュメントメタデータ
  document?: {
    page_count?: number;
    title?: string;
    author?: string;
    created_date?: string;
    modified_date?: string;
    language?: string;
  };
  
  // AIメタデータ
  ai_analysis?: {
    content_type?: string;
    detected_objects?: string[];
    detected_text?: string;
    sentiment?: string;
    confidence_scores?: Record<string, number>;
    analysis_date: string;
  };
}
```

### FileVersion
```typescript
// ファイルバージョン
interface FileVersion {
  // バージョンID
  version_id: string;
  
  // ファイルID
  file_id: string;
  
  // バージョン番号
  version_number: number;
  
  // ファイルパス
  file_path: string;
  
  // ファイルサイズ
  file_size: number;
  
  // ファイルハッシュ
  file_hash: string;
  
  // 変更内容
  change_description?: string;
  
  // 変更者
  changed_by: string;
  
  // 変更日時
  changed_at: string;
  
  // 現在バージョン
  is_current: boolean;
  
  // 復元可能
  can_restore: boolean;
}
```

### FilePermission
```typescript
// ファイル権限
interface FilePermission {
  // ファイルID
  file_id: string;
  
  // 権限付与対象
  grantee: {
    type: 'user' | 'group' | 'role' | 'public';
    id: string;
    name?: string;
  };
  
  // 権限レベル
  permission_level: 'read' | 'write' | 'delete' | 'share' | 'full_control';
  
  // 具体的権限
  permissions: {
    can_view: boolean;
    can_download: boolean;
    can_edit: boolean;
    can_delete: boolean;
    can_share: boolean;
    can_manage_permissions: boolean;
  };
  
  // 有効期限
  expires_at?: string;
  
  // 付与者
  granted_by: string;
  
  // 付与日時
  granted_at: string;
  
  // 条件
  conditions?: {
    ip_restrictions?: string[];
    time_restrictions?: {
      start_time?: string;
      end_time?: string;
      days_of_week?: number[];
    };
    download_limit?: number;
  };
}
```

## ストレージ管理

### StorageProvider
```typescript
// ストレージプロバイダー設定
interface StorageProvider {
  // プロバイダーID
  provider_id: string;
  
  // プロバイダー名
  name: string;
  
  // プロバイダータイプ
  type: 'aws_s3' | 'azure_blob' | 'gcp_cloud_storage' | 'minio' | 'local';
  
  // 接続設定
  connection: {
    // AWS S3
    aws?: {
      region: string;
      access_key_id?: string;
      secret_access_key?: string;
      session_token?: string;
      use_iam_role?: boolean;
      endpoint_url?: string; // MinIOなどのS3互換
    };
    
    // Azure Blob Storage
    azure?: {
      account_name: string;
      account_key?: string;
      connection_string?: string;
      container_name: string;
    };
    
    // Google Cloud Storage
    gcp?: {
      project_id: string;
      key_file?: string;
      credentials?: any;
      bucket_name: string;
    };
    
    // ローカルストレージ
    local?: {
      base_path: string;
      permissions?: string;
    };
  };
  
  // デフォルトバケット
  default_bucket: string;
  
  // 暗号化設定
  encryption?: {
    enabled: boolean;
    method: 'AES256' | 'aws:kms' | 'customer_key';
    kms_key_id?: string;
    customer_key?: string;
  };
  
  // 圧縮設定
  compression?: {
    enabled: boolean;
    algorithm: 'gzip' | 'lz4' | 'snappy';
    level?: number;
  };
  
  // 有効状態
  is_enabled: boolean;
  
  // 優先度
  priority: number;
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
}
```

### StorageBucket
```typescript
// ストレージバケット
interface StorageBucket {
  // バケットID
  bucket_id: string;
  
  // バケット名
  bucket_name: string;
  
  // プロバイダーID
  provider_id: string;
  
  // リージョン
  region?: string;
  
  // 用途
  purpose: 'user_files' | 'system_files' | 'temp_files' | 'backup_files' | 'processed_files';
  
  // アクセス制御
  access_control: {
    default_acl: 'private' | 'public-read' | 'public-read-write';
    cors_enabled: boolean;
    cors_rules?: Array<{
      allowed_origins: string[];
      allowed_methods: string[];
      allowed_headers?: string[];
      max_age_seconds?: number;
    }>;
  };
  
  // ライフサイクル設定
  lifecycle_rules?: Array<{
    rule_id: string;
    enabled: boolean;
    prefix?: string;
    expiration_days?: number;
    transition_rules?: Array<{
      storage_class: string;
      days: number;
    }>;
  }>;
  
  // バージョニング
  versioning: {
    enabled: boolean;
    max_versions?: number;
  };
  
  // 統計情報
  statistics?: {
    total_objects: number;
    total_size_bytes: number;
    last_updated: string;
  };
  
  // 作成日時
  created_at: string;
  
  // 更新日時
  updated_at: string;
}
```

### StorageQuota
```typescript
// ストレージクォータ
interface StorageQuota {
  // ユーザーまたは組織ID
  entity_id: string;
  
  // エンティティタイプ
  entity_type: 'user' | 'organization' | 'project';
  
  // 総容量制限（バイト）
  total_quota_bytes: number;
  
  // 使用容量（バイト）
  used_bytes: number;
  
  // 利用可能容量（バイト）
  available_bytes: number;
  
  // ファイル数制限
  file_count_limit?: number;
  
  // 現在のファイル数
  current_file_count: number;
  
  // 単一ファイルサイズ制限
  max_file_size_bytes?: number;
  
  // ファイルタイプ別制限
  file_type_limits?: Array<{
    mime_type_pattern: string;
    max_size_bytes?: number;
    max_count?: number;
  }>;
  
  // 警告閾値
  warning_thresholds: {
    storage_percentage: number;
    file_count_percentage?: number;
  };
  
  // 現在の使用率
  usage_percentage: number;
  
  // 警告状態
  is_warning: boolean;
  
  // 制限到達状態
  is_exceeded: boolean;
  
  // 最終更新日時
  last_updated: string;
}
```

## ファイル操作

### FileUploadRequest
```typescript
// ファイルアップロードリクエスト
interface FileUploadRequest {
  // ファイル名
  filename: string;
  
  // ファイルサイズ
  file_size: number;
  
  // MIMEタイプ
  mime_type: string;
  
  // ファイルハッシュ（重複チェック用）
  file_hash?: string;
  
  // アップロード先バケット
  bucket?: string;
  
  // ファイルパス（ディレクトリ構造）
  path?: string;
  
  // アップロード方式
  upload_method: 'direct' | 'multipart' | 'presigned_url' | 'resumable';
  
  // マルチパート設定
  multipart_config?: {
    chunk_size: number;
    max_chunks: number;
  };
  
  // 再開可能アップロード設定
  resumable_config?: {
    session_id?: string;
    offset?: number;
  };
  
  // 公開設定
  visibility?: 'private' | 'public' | 'shared';
  
  // タグ
  tags?: string[];
  
  // メタデータ
  metadata?: Record<string, any>;
  
  // 処理オプション
  processing_options?: {
    // 自動画像最適化
    auto_optimize_images?: boolean;
    
    // サムネイル生成
    generate_thumbnails?: boolean;
    
    // ウイルススキャン
    virus_scan?: boolean;
    
    // AI解析
    ai_analysis?: boolean;
  };
  
  // 権限設定
  initial_permissions?: Array<{
    grantee_type: 'user' | 'group' | 'role';
    grantee_id: string;
    permission_level: string;
  }>;
}
```

### FileUploadResponse
```typescript
// ファイルアップロードレスポンス
interface FileUploadResponse {
  // 成功フラグ
  success: boolean;
  
  // ファイル情報
  file?: File;
  
  // アップロード方式別情報
  upload_info?: {
    // 直接アップロード
    direct_upload?: {
      upload_url: string;
      headers?: Record<string, string>;
    };
    
    // マルチパートアップロード
    multipart_upload?: {
      upload_id: string;
      presigned_urls: Array<{
        part_number: number;
        upload_url: string;
        headers?: Record<string, string>;
      }>;
    };
    
    // 署名付きURL
    presigned_url?: {
      upload_url: string;
      expires_at: string;
      headers?: Record<string, string>;
    };
    
    // 再開可能アップロード
    resumable_upload?: {
      session_id: string;
      upload_url: string;
      resume_offset?: number;
      chunk_size: number;
    };
  };
  
  // 重複ファイル情報
  duplicate_file?: {
    file_id: string;
    message: string;
    action: 'use_existing' | 'create_version' | 'overwrite';
  };
  
  // エラー情報
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}
```

### FileDownloadRequest
```typescript
// ファイルダウンロードリクエスト
interface FileDownloadRequest {
  // ファイルID
  file_id: string;
  
  // バージョンID（特定バージョンをダウンロードする場合）
  version_id?: string;
  
  // ダウンロード方式
  download_method: 'direct' | 'presigned_url' | 'streaming' | 'zip_archive';
  
  // レンジダウンロード
  range?: {
    start: number;
    end?: number;
  };
  
  // 変換オプション
  conversion?: {
    format?: string;
    quality?: number;
    size?: { width: number; height: number };
    compression?: string;
  };
  
  // ZIP archive設定（複数ファイル）
  archive_config?: {
    file_ids: string[];
    archive_name: string;
    compression_level?: number;
  };
  
  // アクセス制御
  access_token?: string;
  
  // 有効期限（署名付きURL）
  expires_in?: number;
  
  // ダウンロード用途
  purpose?: 'view' | 'download' | 'processing' | 'backup';
  
  // 監査ログ記録
  audit_download?: boolean;
}
```

### FileDownloadResponse
```typescript
// ファイルダウンロードレスポンス
interface FileDownloadResponse {
  // 成功フラグ
  success: boolean;
  
  // ダウンロード情報
  download_info?: {
    // 直接ダウンロード
    direct_download?: {
      url: string;
      headers?: Record<string, string>;
    };
    
    // 署名付きURL
    presigned_url?: {
      download_url: string;
      expires_at: string;
      headers?: Record<string, string>;
    };
    
    // ストリーミング
    streaming?: {
      stream_url: string;
      content_type: string;
      content_length: number;
    };
    
    // ZIPアーカイブ
    archive?: {
      download_url: string;
      file_count: number;
      total_size: number;
      expires_at: string;
    };
  };
  
  // ファイル情報
  file_info?: {
    filename: string;
    mime_type: string;
    file_size: number;
    last_modified: string;
  };
  
  // エラー情報
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}
```
## API定義

### レスポンス型

```typescript
// 成功レスポンス
interface FileManagementSuccessResponse<T = any> {
  success: true;
  data: T;
  metadata?: {
    timestamp: string;
    request_id: string;
    pagination?: {
      page: number;
      size: number;
      total: number;
      has_next: boolean;
    };
  };
}

// ページネーション付きファイルリスト
interface PaginatedFilesResponse {
  files: File[];
  pagination: {
    page: number;
    size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
  filters_applied?: {
    mime_types?: string[];
    date_range?: { start: string; end: string };
    tags?: string[];
    search_query?: string;
  };
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}
```

### エラー型

```typescript
// エラーレスポンス
interface FileManagementErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: any;
    field_errors?: Array<{
      field: string;
      message: string;
      code: string;
    }>;
    timestamp: string;
    request_id: string;
  };
}

// エラーコード
type FileManagementErrorCode = 
  | 'FILE_NOT_FOUND'
  | 'FILE_ALREADY_EXISTS'
  | 'INVALID_FILE_TYPE'
  | 'FILE_TOO_LARGE'
  | 'QUOTA_EXCEEDED'
  | 'UPLOAD_FAILED'
  | 'DOWNLOAD_FAILED'
  | 'CONVERSION_FAILED'
  | 'INVALID_FILE_FORMAT'
  | 'VIRUS_DETECTED'
  | 'PERMISSION_DENIED'
  | 'STORAGE_UNAVAILABLE'
  | 'BUCKET_NOT_FOUND'
  | 'INVALID_CREDENTIALS'
  | 'NETWORK_ERROR'
  | 'TIMEOUT_ERROR'
  | 'RATE_LIMIT_EXCEEDED'
  | 'MULTIPART_UPLOAD_FAILED'
  | 'PRESIGNED_URL_EXPIRED'
  | 'CHECKSUM_MISMATCH'
  | 'INSUFFICIENT_STORAGE'
  | 'CONCURRENT_MODIFICATION'
  | 'VALIDATION_ERROR'
  | 'PROCESSING_ERROR';
```
EOF < /dev/null
