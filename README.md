# MAKOTO Visual AI

AI駆動型ビジュアルアシスタントプラットフォーム

## 概要

MAKOTO Visual AIは、マルチモーダルAI技術を活用した次世代のビジュアルアシスタントプラットフォームです。テキスト、画像、音声を統合的に処理し、ユーザーに直感的で強力なAI体験を提供します。

## 主な機能

- 🤖 **マルチモーダルAI対話** - テキスト、画像、音声を統合した対話システム
- 📚 **ナレッジライブラリ** - 構造化された知識ベースの管理と活用
- 🔄 **ワークフローチェイン** - 複数のAIエージェントを連携させた処理フロー
- 🎯 **タスク管理** - AI支援によるタスク実行と進捗管理
- 🌐 **Webクロール** - 情報収集と分析の自動化
- 🔌 **プラグインシステム** - 機能拡張可能なアーキテクチャ

## アーキテクチャ

### マルチクラウド・マルチテナント対応

- **AWS** / **Azure** / **オンプレミス** での動作をサポート
- テナントごとに独立したリソース管理
- テナント提供型のLLMサービス接続（OpenAI、Azure OpenAI、Claude等）

### 技術スタック

- **バックエンド**: Python (FastAPI) + Lambda
- **フロントエンド**: Next.js + TypeScript
- **データベース**: DynamoDB / CosmosDB
- **認証**: AWS Cognito / Azure AD
- **AI/ML**: OpenAI API、Azure OpenAI、Anthropic Claude

## ディレクトリ構造

```
makoto/
├── backend/           # バックエンドコード
│   ├── layers/       # Lambda Layer（共通ライブラリ）
│   ├── functions/    # Lambda関数
│   └── api/          # FastAPI アプリケーション
├── frontend/         # フロントエンドコード
│   ├── src/         # ソースコード
│   └── public/      # 静的ファイル
├── infrastructure/   # インフラ定義
│   ├── terraform/   # Terraform設定
│   └── cloudformation/ # CloudFormationテンプレート
└── docs/            # ドキュメント
    ├── API型定義/   # API仕様書
    └── layers/      # Lambda Layer設計書
```

## セットアップ

### 前提条件

- Python 3.11+
- Node.js 18+
- AWS CLI設定済み（AWS環境の場合）
- Azure CLI設定済み（Azure環境の場合）

### Lambda Layer のビルド

```bash
cd backend/layers/common
./build.sh
```

### ローカル開発環境

```bash
# バックエンド
cd backend/api
pip install -r requirements.txt
uvicorn main:app --reload

# フロントエンド
cd frontend
npm install
npm run dev
```

## ドキュメント

詳細なドキュメントは [docs/](./docs/) ディレクトリを参照してください。

- [API型定義](./docs/API型定義/)
- [Lambda Layer設計](./docs/layers/)
- [SaaS基盤アーキテクチャ](./docs/SaaS基盤アーキテクチャ設計書.md)

## ライセンス

Proprietary

## お問い合わせ

MAKOTO Visual AI チーム