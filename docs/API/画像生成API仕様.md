# 画像生成API仕様

## 概要
Azure OpenAIの画像生成モデル（デプロイメント名: gpt-image-1）を使用した画像生成APIの詳細仕様書。

## エンドポイント

### 画像生成

**エンドポイント:** `POST /api/images/generate`

**説明:** テキストプロンプトから画像を生成します。生成された画像はサーバーに保存され、アクセス可能なURLが返されます。

**リクエストボディ:**
```json
{
  "prompt": "美しい蝶のイラスト",
  "n": 1,
  "size": "1024x1024",
  "quality": "medium",
  "output_format": "url"
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| prompt | string | ✓ | - | 画像生成のプロンプト |
| n | integer | - | 1 | 生成する画像の数 |
| size | string | - | "1024x1024" | 画像サイズ |
| quality | string | - | "medium" | 画質 |
| output_format | string | - | "url" | 出力形式 |

**サイズオプション:**
- `"1024x1024"`: 正方形（デフォルト）
- `"1792x1024"`: 横長
- `"1024x1792"`: 縦長

**画質オプション:**
- `"medium"`: 標準画質
- `"hd"`: 高画質

**出力形式:**
- `"url"`: URLとして返す（推奨）
- `"b64_json"`: Base64エンコード（Azure APIの内部処理用）

## レスポンス

### 成功時 (200 OK)
```json
{
  "success": true,
  "images": [
    {
      "url": "/uploads/generated_images/美しい蝶のイラスト_abc123.png",
      "file_path": "/path/to/image.png",
      "filename": "美しい蝶のイラスト_abc123.png",
      "created_at": "2025-07-10T10:30:00"
    }
  ],
  "prompt": "美しい蝶のイラスト"
}
```

**レスポンスフィールド:**
| フィールド | 型 | 説明 |
|-----------|-----|------|
| success | boolean | 処理の成功/失敗 |
| images | array | 生成された画像の配列 |
| images[].url | string | 画像の相対URL |
| images[].file_path | string | サーバー上の絶対パス |
| images[].filename | string | ファイル名 |
| images[].created_at | string | 生成日時（ISO 8601形式） |
| prompt | string | 使用されたプロンプト |

### エラー時
```json
{
  "success": false,
  "error": "画像生成エラー: API rate limit exceeded",
  "prompt": "美しい蝶のイラスト"
}
```

## 画像へのアクセス

生成された画像は以下のURLパターンでアクセスできます：

```
http://localhost:8000/uploads/generated_images/{filename}
```

**例:**
```
http://localhost:8000/uploads/generated_images/美しい蝶のイラスト_abc123.png
```

## 使用例

### cURLコマンド
```bash
curl -X POST http://localhost:8000/api/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "夕日に照らされた富士山の風景画",
    "quality": "hd",
    "size": "1792x1024"
  }'
```

### JavaScriptフェッチ
```javascript
async function generateImage(prompt) {
  try {
    const response = await fetch('http://localhost:8000/api/images/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        quality: 'medium',
        size: '1024x1024'
      })
    });

    const data = await response.json();
    
    if (data.success) {
      const imageUrl = `http://localhost:8000${data.images[0].url}`;
      console.log('画像生成成功:', imageUrl);
      return imageUrl;
    } else {
      console.error('画像生成失敗:', data.error);
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('リクエストエラー:', error);
    throw error;
  }
}

// 使用例
generateImage('美しい夕焼けの海岸線')
  .then(imageUrl => {
    // 画像を表示
    const img = document.createElement('img');
    img.src = imageUrl;
    document.body.appendChild(img);
  })
  .catch(error => {
    alert('画像生成に失敗しました: ' + error.message);
  });
```

## Azure OpenAI設定

### デプロイメント情報
- **モデル名**: gpt-image-1
- **エンドポイント**: `https://makoto-img.openai.azure.com/openai/deployments/gpt-image-1/images/generations`
- **APIバージョン**: `2025-04-01-preview`

### 環境変数設定
```env
AZURE_OPENAI_IMAGE_ENDPOINT=https://makoto-img.openai.azure.com/openai/deployments/gpt-image-1/images/generations?api-version=2025-04-01-preview
AZURE_OPENAI_IMAGE_API_KEY=your-api-key-here
```

## 内部処理フロー

1. **リクエスト受信**: FastAPIエンドポイントがリクエストを受信
2. **パラメータ検証**: Pydanticによる自動バリデーション
3. **Azure API呼び出し**: 
   - エンドポイント: 環境変数`AZURE_OPENAI_IMAGE_ENDPOINT`
   - APIキー: 環境変数`AZURE_OPENAI_IMAGE_API_KEY`
   - ヘッダー: `Api-Key`を使用（`Authorization`ではない）
4. **レスポンス処理**:
   - `output_format`が`"png"`の場合: Base64データが返される
   - Base64データをデコードしてPNG画像として保存
5. **ファイル保存**: 
   - ディレクトリ: `uploads/generated_images/`
   - ファイル名: `{プロンプト前30文字}_{UUID}.png`
6. **レスポンス返却**: 保存された画像のURLを含むJSONレスポンス

## エラーハンドリング

### 一般的なエラー

1. **APIキー未設定**
```json
{
  "success": false,
  "error": "Image generation API key not configured"
}
```

2. **レート制限超過**
```json
{
  "success": false,
  "error": "画像生成エラー: API rate limit exceeded"
}
```

3. **タイムアウト**
```json
{
  "success": false,
  "error": "Request timed out"
}
```

4. **不正なパラメータ**
```json
{
  "detail": [
    {
      "loc": ["body", "size"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum"
    }
  ]
}
```

## 制限事項

1. **生成枚数**: 1リクエストにつき1枚まで
2. **ファイルサイズ**: 生成される画像は通常1-5MB
3. **レート制限**: Azure OpenAIの制限に準拠
4. **タイムアウト**: 120秒（aiohttp設定）

## セキュリティ考慮事項

1. **APIキー管理**: 環境変数で管理、コードにハードコーディングしない
2. **ファイル名**: UUIDを使用してファイル名の衝突を防止
3. **アクセス制御**: 現在は認証なし（開発環境）
4. **入力検証**: プロンプトとパラメータの値を検証
5. **CORS**: 設定されたオリジンからのみアクセス可能