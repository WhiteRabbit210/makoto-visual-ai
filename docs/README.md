# MAKOTO Visual AI ドキュメント

## 目次
1. [プロジェクト概要](#プロジェクト概要)
2. [ドキュメント構成](#ドキュメント構成)
3. [クイックスタート](#クイックスタート)
4. [主要機能](#主要機能)
5. [技術スタック](#技術スタック)
6. [関連リンク](#関連リンク)

## プロジェクト概要

MAKOTO Visual AIは、エンタープライズ向けのマルチテナント対応AIアシスタントSaaSプラットフォームです。

### 特徴
- 🏢 **マルチテナント対応**: 完全なテナント分離とセキュリティ
- 🤖 **AIエージェント**: 高度な対話型AIアシスタント
- 📊 **データ分析**: Parquet形式での分析基盤
- ☁️ **マルチクラウド**: AWS/Azure両対応
- 🔒 **エンタープライズセキュリティ**: 認証認可、監査ログ完備

## ドキュメント構成

### 📋 仕様書
- [チャット仕様書](仕様書/チャット仕様書.md) - チャット機能の詳細仕様
- [エージェント仕様書](仕様書/エージェント仕様書.md) - AIエージェントの仕様
- [データ保存仕様書](仕様書/データ保存仕様書.md) - ストレージとKVM連携
- [ページネーション仕様](仕様書/チャットAPIページネーション仕様.md) - 大規模データ対応

### 🔌 API仕様
- [チャットAPI](API/チャットAPI仕様.md) - チャット関連のAPIエンドポイント
- [エージェントAPI](API/エージェントAPI仕様.md) - エージェント制御API
- [タスク管理API](API/タスク管理API仕様.md) - タスク実行と管理
- [WebクロールAPI](仕様書/型定義/WebクロールAPI型定義.md) - Web情報取得

### 📐 型定義
- [共通型定義](仕様書/型定義/共通型定義.md) - 基本的な型定義
- [チャットAPI型](仕様書/型定義/チャットAPI型定義.md) - チャットAPI用の型
- [エージェントAPI型](仕様書/型定義/エージェントAPI型定義.md) - エージェントAPI用の型

### 🏗️ アーキテクチャ
- [SaaS基盤設計](SaaS基盤アーキテクチャ設計書.md) - マルチテナントSaaS設計
- [Azure OpenAI統合](Azure_OpenAI統合設計書.md) - AI基盤の統合設計
- [認証認可設計](認証認可設計書.md) - セキュリティ設計
- [データベース抽象化](仕様書/layers_データベース抽象化設計.md) - DB層の設計

### 🎨 UI仕様
- [チャット画面](UI/チャット画面仕様.md) - チャットUIの仕様
- [タスク管理画面](UI/タスク管理画面仕様.md) - タスク管理UIの仕様
- [デザインシステム](UI/デザインシステム.md) - UIコンポーネント設計

## クイックスタート

### 1. 環境構築

```bash
# リポジトリのクローン
git clone https://github.com/WhiteRabbit210/makoto-visual-ai.git
cd makoto-visual-ai/makoto

# バックエンド環境構築
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# フロントエンド環境構築
cd ../frontend
npm install
```

### 2. 環境変数設定

```bash
# backend/.env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=your-endpoint
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

### 3. ローカル実行

```bash
# バックエンド起動
cd backend
python main.py

# フロントエンド起動（別ターミナル）
cd frontend
npm run dev
```

アプリケーション: http://localhost:5173

## 主要機能

### チャット機能
- リアルタイムメッセージング
- メッセージ履歴管理
- ページネーション対応（50件/ページ）
- room_idベースの管理

### エージェント機能
- Function Calling対応（GPT-4.1）
- JSONモード対応（GPT-5）
- Webクロール統合
- 画像生成連携

### データ管理
- **KVM（Key-Value Management）**: DynamoDB/CosmosDB対応
- **BlobStorage/S3**: 全メッセージ保存
- **Parquet変換**: 日次バッチ処理で分析用データ生成
- **ローカルインデックス**: TinyDBでキャッシュ管理

### マルチテナント
- 完全なテナント分離
- テナント別リソース管理
- 階層型ディレクトリ構造

## 技術スタック

### バックエンド
- **言語**: Python 3.11
- **フレームワーク**: FastAPI
- **AI**: Azure OpenAI (GPT-4.1)
- **データベース**: DynamoDB/CosmosDB
- **ストレージ**: S3/BlobStorage

### フロントエンド
- **言語**: TypeScript
- **フレームワーク**: React 18 + Vite
- **UI**: Tailwind CSS
- **状態管理**: React Hooks

### インフラ
- **AWS**: Lambda, EventBridge, S3, DynamoDB
- **Azure**: Functions, BlobStorage, CosmosDB
- **分析**: Athena/Synapse Analytics

## 関連リンク

### 内部ドキュメント
- [開発者ガイド](backend/CLAUDE.md) - 開発時の注意事項
- [テスト結果](backend/tests/テスト実行結果.md) - 最新のテスト状況
- [デプロイガイド](backend/cloud_functions/deployment_guide.md) - デプロイ手順

### 外部リソース
- [GitHub リポジトリ](https://github.com/WhiteRabbit210/makoto-visual-ai)
- [Azure OpenAI ドキュメント](https://learn.microsoft.com/azure/cognitive-services/openai/)
- [AWS Lambda ドキュメント](https://docs.aws.amazon.com/lambda/)

## ドキュメント整理状況

⚠️ **注意**: ドキュメントの整理を進めています。詳細は[ドキュメント整理案](ドキュメント整理案.md)を参照してください。

### 現在の課題
1. ドキュメントの分散
2. 日本語/英語名の混在
3. 重複内容の存在

### 改善予定
- ディレクトリ構造の再編成
- 日本語名への統一
- 目次とナビゲーションの充実

---

**最終更新**: 2025年8月12日  
**バージョン**: 1.0.0  
**メンテナー**: MAKOTO開発チーム