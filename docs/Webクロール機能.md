# Webクロール機能

## 概要
エージェントAIがユーザーの質問を分析し、最新情報が必要と判断した場合に自動的にWeb検索・クロールを実行し、エビデンスに基づいた回答を提供する機能です。

## 機能フロー

1. **エージェント分析**
   - ユーザーの質問を分析
   - Webクロールが必要かを判定
   - 必要な場合はGoogle検索キーワードを生成（3-5個）

2. **Web検索・クロール**
   - Google Custom Search APIで検索実行（上位5件）
   - 各URLの内容をクロール
   - 不要な要素（スクリプト、スタイル等）を除去
   - 主要コンテンツを抽出

3. **要約・統合**
   - クロール結果をLLMで要約
   - 元の質問に関連する情報を抽出
   - 要約結果をコンテキストに追加

4. **回答生成**
   - クロール結果を含めてLLMが回答生成
   - エビデンスURLをメッセージに添付

## 実装詳細

### バックエンド

#### 1. エージェントAPI (`api/agent.py`)
- `ModeAnalysis`モデルに`search_keywords`フィールドを追加
- Function Callingで検索キーワードを生成

```python
class ModeAnalysis(BaseModel):
    type: str  # "web", "image", "rag", "none"
    confidence: float
    reason: str
    search_keywords: Optional[List[str]] = None  # Webモード時のGoogle検索キーワード
```

#### 2. Webクロールサービス (`services/web_crawler_service.py`)
- Google Custom Search API統合
- 非同期Web scraping（aiohttp + BeautifulSoup）
- コンテンツ抽出と要約

主要メソッド：
- `search_and_crawl()`: 検索とクロールの統合処理
- `_google_search()`: Google検索実行
- `_crawl_url()`: 個別URLのクロール
- `_extract_main_content()`: 主要コンテンツ抽出
- `_summarize_contents()`: LLMによる要約

#### 3. WebクロールAPI (`api/webcrawl.py`)
- RESTful APIエンドポイント
- `/api/webcrawl/crawl`: クロール実行

### フロントエンド

#### 1. 型定義の拡張
- `ModeAnalysis`に`search_keywords`追加
- `Message`に`crawl_sources`追加

#### 2. エビデンスURL表示 (`MessageItem.tsx`)
- クロール参照元をメッセージ下部に表示
- 各URLはリンク化され、新規タブで開く
- スニペット（抜粋）も表示

```tsx
{/* Webクロール参照元 - エビデンスURL */}
{!isUser && message.crawl_sources && message.crawl_sources.length > 0 && (
  <div className="mt-3 w-[80%] ml-[2.75rem]">
    <div className="bg-surface/50 rounded-lg p-4 border border-border">
      <p className="text-sm font-medium text-text-secondary mb-2">📌 参照元</p>
      {/* URLリンクとスニペット表示 */}
    </div>
  </div>
)}
```

## 環境設定

### 必要な環境変数（.env）
```bash
# Google Custom Search API
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
```

### 必要なパッケージ
- `beautifulsoup4`: HTMLパース
- `aiohttp`: 非同期HTTPクライアント
- `pytz`: タイムゾーン処理

## 使用例

1. ユーザー: 「ミツイワ株式会社の現在の社長は誰ですか？」
2. エージェント: Webクロールモードを推奨、検索キーワード生成
3. システム: Google検索実行、上位サイトをクロール
4. システム: 情報を要約してLLMに提供
5. AI: クロール結果に基づいて回答、参照元URLを表示

## 注意事項

- Google Custom Search APIは無料枠に制限あり（100クエリ/日）
- 開発環境ではAPIキー未設定時にダミーデータを使用
- クロール対象サイトのrobot.txtは考慮していない（実装予定）
- 1ページあたり最大5000文字に制限