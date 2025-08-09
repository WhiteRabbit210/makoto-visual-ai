# ChatGPT連携API仕様

## 概要
Azure OpenAI ChatGPTとの連携APIの詳細仕様書。テキスト生成と画像生成（DALL-E 3）の統合機能を提供します。

## エンドポイント一覧

### 1. 単一レスポンス生成

**エンドポイント:** `POST /api/chat/completion`

**説明:** ChatGPTに単一のレスポンスを生成させます。ストリーミングなしの同期処理です。

**リクエストボディ:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "富士山について教えてください"
    }
  ],
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "active_modes": ["webcrawl", "rag"]
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| messages | array | ✓ | - | チャットメッセージの配列 |
| model | string | - | "gpt-4" | 使用するモデル |
| temperature | float | - | 0.7 | 生成の創造性（0-2） |
| max_tokens | integer | - | 1000 | 最大トークン数 |
| active_modes | array | - | [] | 有効なモード |

**active_modesの値:**
- `"webcrawl"`: Webクロールモード
- `"image"`: 画像生成モード
- `"rag"`: RAG（Retrieval-Augmented Generation）モード

**レスポンス例:**
```json
{
  "message": {
    "role": "assistant",
    "content": "富士山は日本最高峰の山で、標高3,776メートルです。静岡県と山梨県の境界に位置し、日本の象徴として親しまれています。",
    "timestamp": "2025/07/10 10:00:00"
  },
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 150,
    "total_tokens": 200
  }
}
```

### 2. ストリーミングレスポンス生成

**エンドポイント:** `POST /api/chat/stream`

**説明:** ChatGPTによるテキスト生成をリアルタイムでストリーミングします。`active_modes`に`"image"`が含まれる場合、テキスト生成後に自動的に画像生成も行います。

**リクエストボディ:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "美しい蝶の画像を生成してください"
    }
  ],
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": true,
  "active_modes": ["image"],
  "chat_id": "optional-chat-id"
}
```

**パラメータ:**
| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|-----|------|------------|------|
| messages | array | ✓ | - | チャットメッセージの配列 |
| model | string | - | "gpt-4" | 使用するモデル |
| temperature | float | - | 0.7 | 生成の創造性（0-2） |
| max_tokens | integer | - | 1000 | 最大トークン数 |
| stream | boolean | - | false | ストリーミング有効化（通常true） |
| active_modes | array | - | [] | 有効なモード |
| chat_id | string | - | null | 既存チャットのID |

**レスポンス形式:** Server-Sent Events (SSE)

#### イベントタイプ

1. **テキストチャンク**
```
data: {"content": "こんにちは"}
data: {"content": "。"}
data: {"content": "美しい"}
```

2. **画像生成開始通知**
```
data: {"generating_image": true}
```

3. **画像生成完了**
```
data: {"images": [
  {
    "url": "/uploads/generated_images/美しい蝶_abc123.png",
    "prompt": "美しい蝶の画像を生成してください",
    "created_at": "2025-07-10T10:30:00"
  }
]}
```

4. **画像生成エラー**
```
data: {"image_error": "画像生成に失敗しました: API rate limit exceeded"}
```

5. **ストリーミング完了**
```
data: {"done": true, "chat_id": "abc-123-def"}
```

### JavaScript実装例

```javascript
async function streamChat() {
  const response = await fetch('http://localhost:8000/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages: [
        { role: 'user', content: '夕日の風景を描いてください' }
      ],
      active_modes: ['image'],
      temperature: 0.7,
      stream: true
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        if (data.content) {
          // テキストの追加
          console.log('Text:', data.content);
          appendToChat(data.content);
        } else if (data.generating_image) {
          console.log('画像生成中...');
          showImageGeneratingIndicator();
        } else if (data.images) {
          console.log('画像生成完了:', data.images);
          displayImages(data.images);
        } else if (data.image_error) {
          console.error('画像生成エラー:', data.image_error);
          showError(data.image_error);
        } else if (data.done) {
          console.log('完了、チャットID:', data.chat_id);
          onComplete(data.chat_id);
        }
      }
    }
  }
}
```

## 画像生成の動作仕様

### 画像生成モードの動作

1. **トリガー条件**: `active_modes`配列に`"image"`が含まれている場合
2. **プロンプト**: ユーザーの最新メッセージ全体を画像生成プロンプトとして使用
3. **生成タイミング**: テキスト応答の完了後
4. **生成枚数**: 1枚（DALL-E 3の制限）

### 画像生成パラメータ（固定値）
- **サイズ**: 1024x1024
- **品質**: medium
- **モデル**: DALL-E 3（Azure OpenAI経由）

## エラーハンドリング

### HTTPステータスコード
- `200`: 成功
- `500`: サーバーエラー（API呼び出しエラー等）

### エラーレスポンス例
```json
{
  "detail": "ChatGPT API呼び出しエラー: Connection timeout"
}
```

### ストリーミング中のエラー
ストリーミング中にエラーが発生した場合、エラーイベントがSSEで送信されます：
```
data: {"error": "エラーメッセージ"}
```

## モックモード

開発時は環境変数`USE_MOCK_CHATGPT=true`でモックモードを有効化できます。

### モックレスポンスの特徴
1. 1秒の遅延後にレスポンス
2. リクエスト内容を含むモック応答を生成
3. アクティブモードを応答に含める
4. ストリーミングモードでは文字単位で送信（タイピング効果）

## 注意事項

1. **ストリーミングAPIの推奨**: リアルタイム性とユーザー体験向上のため、通常はストリーミングAPIの使用を推奨

2. **チャット履歴の自動保存**: ストリーミングAPIでは応答完了時に自動的にチャット履歴が保存されます

3. **画像生成の非同期性**: 画像生成は時間がかかるため、テキスト応答とは独立して処理されます

4. **レート制限**: Azure OpenAIのレート制限に準拠。詳細はAzureのドキュメントを参照

5. **トークン数の管理**: `max_tokens`パラメータで応答の長さを制御できます