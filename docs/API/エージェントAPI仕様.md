# エージェントAPI仕様

## 概要
エージェント機能は、ユーザーのプロンプトを分析し、最適な回答方法（Webクロール、画像生成、RAGなど）を自動的に判定するAI機能です。

## エンドポイント

### POST /api/agent/analyze
プロンプトを分析して必要なモードを判定

#### リクエスト
```json
{
  "prompt": "string",           // 分析対象のプロンプト（必須）
  "context": [                  // 過去の会話コンテキスト（オプション）
    {
      "role": "user | assistant",
      "content": "string"
    }
  ]
}
```

#### レスポンス
```json
{
  "modes": [                    // 判定されたモードのリスト
    {
      "type": "web | image | rag | none",  // モードタイプ
      "confidence": 0.8,                    // 確信度（0-1）
      "reason": "string"                    // 判定理由
    }
  ],
  "analysis": "string",         // プロンプトの全体的な分析
  "primary_mode": "string"      // 最も確信度の高いモード
}
```

## モードタイプ

### web（Webクロール）
以下の場合に判定される：
- 最新情報が必要な質問
- 特定の企業・人物の現在の情報
- リアルタイムデータ（株価、天気、ニュース等）
- ナレッジカットオフ以降の情報
- ハルシネーションのリスクが高い具体的な事実

### image（画像生成）
以下の場合に判定される：
- 画像、イラスト、図の作成・生成の要求
- ビジュアル表現、デザインの依頼
- 「描いて」「作って」などの画像関連動詞

### rag（RAGモード）
以下の場合に判定される：
- アップロードされたドキュメントに関する質問
- 特定の文書を参照する必要がある質問

### none（通常モード）
以下の場合に判定される：
- 一般的な知識で回答可能
- プログラミング、技術的な説明
- 数学的計算、論理的推論

## 使用例

### リクエスト例
```bash
curl -X POST http://localhost:8000/api/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "ミツイワ株式会社の現在の社長は誰ですか？",
    "context": []
  }'
```

### レスポンス例
```json
{
  "modes": [
    {
      "type": "web",
      "confidence": 0.8,
      "reason": "特定企業の現在の人事情報に関する質問のため、最新情報の検索が必要"
    }
  ],
  "analysis": "ユーザーは特定企業（ミツイワ株式会社）の現在の社長について質問しています。このような人事情報は頻繁に変更される可能性があり、最新の情報が必要です。",
  "primary_mode": "web"
}
```

## フロントエンド統合

### エージェントモードの流れ
1. ユーザーがエージェントボタンをONにする
2. メッセージ送信時、バックグラウンドでプロンプトを分析
3. 分析中は「エージェントが分析中...」のUIを表示
4. 分析結果に基づいて自動的にモードを設定
5. 設定されたモードで通常のChatGPT APIを実行

### TypeScript型定義
```typescript
interface ModeAnalysis {
  type: 'web' | 'image' | 'rag' | 'none';
  confidence: number;
  reason: string;
}

interface AnalyzeResponse {
  modes: ModeAnalysis[];
  analysis: string;
  primary_mode?: string;
}
```

## エラーレスポンス

### 400 Bad Request
```json
{
  "detail": "プロンプトは必須です"
}
```

### 500 Internal Server Error
```json
{
  "detail": "エージェント分析エラー: [エラー詳細]"
}
```

## 実装上の注意

1. **キャッシュ**
   - 類似プロンプトの分析結果はキャッシュ可能
   - TTLは1時間程度を推奨

2. **レート制限**
   - エージェント分析は通常のAPIより処理が重い
   - 適切なレート制限の実装を推奨

3. **非同期処理**
   - フロントエンドでは分析を非同期で実行
   - UXを損なわないよう配慮

4. **拡張性**
   - 新しいモードタイプの追加が容易な設計
   - Function Callingのスキーマ更新で対応可能