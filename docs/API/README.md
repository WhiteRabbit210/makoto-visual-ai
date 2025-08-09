# API仕様書ディレクトリ

このディレクトリには、MAKOTO Visual AIの各機能別API仕様書が含まれています。

## ドキュメント一覧

### 基本機能
- [チャットAPI仕様](./チャットAPI仕様.md) - チャット管理の基本CRUD操作
- [ChatGPT連携API仕様](./ChatGPT連携API仕様.md) - Azure OpenAI ChatGPTとの連携、ストリーミング対応
- [画像生成API仕様](./画像生成API仕様.md) - Azure OpenAI画像生成モデル（gpt-image-1）の統合

### 管理機能
- [ライブラリ管理API仕様](./ライブラリ管理API仕様.md) - PDFファイルとドキュメントの管理
- [タスク管理API仕様](./タスク管理API仕様.md) - タスクの作成、管理、アーカイブ機能

### その他（今後追加予定）
- タスクテンプレートAPI仕様
- 設定管理API仕様
- WebSocket通信仕様

## API概要

### ベースURL
```
http://localhost:8000/api
```

### 認証
現在は認証なし（開発環境）

### レスポンス形式
- 通常のAPI: JSON
- ストリーミングAPI: Server-Sent Events (SSE)

### エラーレスポンス
```json
{
  "detail": "エラーメッセージ"
}
```

## 関連ドキュメント
- [../API構造.md](../API構造.md) - API全体の構造と実装状況
- [../API仕様書.md](../API仕様書.md) - 統合版API仕様書（レガシー）

## 更新履歴
- 2025-07-10: 初版作成、機能別にAPI仕様書を分割