# ライブラリ管理API仕様

## 概要
PDFファイルやドキュメントを管理するライブラリ機能のAPI仕様書。

## エンドポイント一覧

### 1. ライブラリ一覧取得

**エンドポイント:** `GET /api/libraries`

**説明:** 登録されているライブラリの一覧を取得します。

**レスポンス例:**
```json
[
  {
    "id": "lib-001",
    "name": "プロジェクトA資料",
    "description": "プロジェクトAに関する技術資料とドキュメント",
    "files": ["technical-spec.pdf", "design-doc.pdf"],
    "file_count": 2,
    "total_size": 5242880,
    "created_at": "2025-07-10T10:00:00",
    "updated_at": "2025-07-10T15:30:00"
  },
  {
    "id": "lib-002",
    "name": "法務関連文書",
    "description": "契約書や法的文書のコレクション",
    "files": ["contract-2025.pdf"],
    "file_count": 1,
    "total_size": 1048576,
    "created_at": "2025-07-09T09:00:00",
    "updated_at": "2025-07-09T09:00:00"
  }
]
```

### 2. ライブラリ詳細取得

**エンドポイント:** `GET /api/libraries/{library_id}`

**説明:** 特定のライブラリの詳細情報を取得します。

**パスパラメータ:**
- `library_id`: ライブラリのID

**レスポンス例:**
```json
{
  "id": "lib-001",
  "name": "プロジェクトA資料",
  "description": "プロジェクトAに関する技術資料とドキュメント",
  "files": [
    {
      "name": "technical-spec.pdf",
      "size": 3145728,
      "pages": 45,
      "uploaded_at": "2025-07-10T10:00:00"
    },
    {
      "name": "design-doc.pdf",
      "size": 2097152,
      "pages": 30,
      "uploaded_at": "2025-07-10T10:05:00"
    }
  ],
  "file_count": 2,
  "total_size": 5242880,
  "created_at": "2025-07-10T10:00:00",
  "updated_at": "2025-07-10T15:30:00",
  "metadata": {
    "tags": ["technical", "project-a"],
    "version": "1.0"
  }
}
```

### 3. ライブラリ作成

**エンドポイント:** `POST /api/libraries`

**説明:** 新しいライブラリを作成します。

**リクエストボディ:**
```json
{
  "name": "新規プロジェクト資料",
  "description": "新規プロジェクトの関連文書",
  "files": [],
  "metadata": {
    "tags": ["new-project"],
    "version": "1.0"
  }
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| name | string | ✓ | ライブラリ名 |
| description | string | - | ライブラリの説明 |
| files | array | - | 初期ファイルリスト |
| metadata | object | - | メタデータ |

**レスポンス例:**
```json
{
  "id": "lib-003",
  "name": "新規プロジェクト資料",
  "description": "新規プロジェクトの関連文書",
  "files": [],
  "file_count": 0,
  "total_size": 0,
  "created_at": "2025-07-10T16:00:00",
  "updated_at": "2025-07-10T16:00:00",
  "metadata": {
    "tags": ["new-project"],
    "version": "1.0"
  }
}
```

### 4. ライブラリ更新

**エンドポイント:** `PUT /api/libraries/{library_id}`

**説明:** ライブラリの情報を更新します。

**パスパラメータ:**
- `library_id`: 更新するライブラリのID

**リクエストボディ:**
```json
{
  "name": "更新されたライブラリ名",
  "description": "更新された説明",
  "metadata": {
    "tags": ["updated", "project-a"],
    "version": "1.1"
  }
}
```

### 5. ライブラリ削除

**エンドポイント:** `DELETE /api/libraries/{library_id}`

**説明:** ライブラリとその関連ファイルを削除します。

**パスパラメータ:**
- `library_id`: 削除するライブラリのID

**レスポンス例:**
```json
{
  "message": "Library deleted successfully",
  "deleted_files": 2
}
```

### 6. ファイルアップロード

**エンドポイント:** `POST /api/libraries/{library_id}/files`

**説明:** ライブラリにファイルをアップロードします。

**パスパラメータ:**
- `library_id`: アップロード先のライブラリID

**リクエスト形式:** multipart/form-data

**フォームフィールド:**
- `file`: アップロードするファイル（PDFのみ対応）

**レスポンス例:**
```json
{
  "filename": "new-document.pdf",
  "size": 1048576,
  "pages": 15,
  "uploaded_at": "2025-07-10T16:30:00",
  "library_id": "lib-001"
}
```

### 7. ファイル削除

**エンドポイント:** `DELETE /api/libraries/{library_id}/files/{filename}`

**説明:** ライブラリから特定のファイルを削除します。

**パスパラメータ:**
- `library_id`: ライブラリID
- `filename`: 削除するファイル名

**レスポンス例:**
```json
{
  "message": "File deleted successfully",
  "filename": "old-document.pdf"
}
```

## データモデル

### Library
```typescript
interface Library {
  id: string;              // ライブラリID
  name: string;            // ライブラリ名
  description?: string;    // 説明
  files: string[] | FileInfo[]; // ファイルリスト
  file_count: number;      // ファイル数
  total_size: number;      // 合計サイズ（バイト）
  created_at: string;      // 作成日時
  updated_at: string;      // 更新日時
  metadata?: {             // メタデータ
    tags?: string[];
    version?: string;
    [key: string]: any;
  };
}
```

### FileInfo
```typescript
interface FileInfo {
  name: string;           // ファイル名
  size: number;          // ファイルサイズ（バイト）
  pages?: number;        // ページ数（PDF）
  uploaded_at: string;   // アップロード日時
}
```

## エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `201`: 作成成功
- `400`: 不正なリクエスト
- `404`: リソースが見つからない
- `413`: ファイルサイズ超過
- `415`: サポートされていないメディアタイプ

### エラーレスポンス例

**404 Not Found:**
```json
{
  "detail": "Library not found"
}
```

**413 Payload Too Large:**
```json
{
  "detail": "File size exceeds maximum allowed size of 100MB"
}
```

**415 Unsupported Media Type:**
```json
{
  "detail": "Only PDF files are supported"
}
```

## 制限事項

1. **ファイル形式**: 現在はPDFファイルのみサポート
2. **ファイルサイズ**: 最大100MB/ファイル
3. **ライブラリ数**: 制限なし（将来的に制限される可能性あり）
4. **ファイル数**: 1ライブラリあたり最大100ファイル

## 注意事項

1. **ファイル保存場所**: `uploads/libraries/{library_id}/`
2. **ファイル名**: アップロード時のオリジナル名を保持
3. **重複チェック**: 同一ライブラリ内での同名ファイルは上書き
4. **削除処理**: ライブラリ削除時は関連ファイルも削除される