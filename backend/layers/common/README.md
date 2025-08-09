# MAKOTO Common Lambda Layer

MAKOTO Visual AI プラットフォームの共通ライブラリLayer

## 概要

このLambda Layerは、MAKOTO Visual AIのバックエンドLambda関数で共通して使用されるライブラリとユーティリティを提供します。

## 機能

### 🏢 マルチテナント管理
- 完全なテナント分離
- テナントコンテキスト管理
- リソースアクセス制御

### 💾 データベース抽象化
- DynamoDB/CosmosDB対応
- 統一されたクエリインターフェース
- 自動テナントフィルタリング

### 🤖 AI標準化
- OpenAI/Azure OpenAI統合
- ストリーミング応答対応
- プロンプト管理

### 📨 イベント処理
- イベント駆動アーキテクチャ
- ローカル/SQS/EventBridge対応
- ドメインイベント定義

### ✅ バリデーション
- カスタムバリデーター
- 複合バリデーション
- 日本語対応

## インストール

### Lambda Layerとして使用

```bash
# ビルド
./build.sh

# デプロイ
./deploy.sh dev ap-northeast-1
```

### ローカル開発

```bash
pip install -r requirements.txt
```

## 使用方法

### テナント管理

```python
from makoto_common.tenant import get_tenant_manager

manager = get_tenant_manager()
manager.load_config(tenant_config)
db = manager.get_database_client()
```

### データベース操作

```python
from makoto_common.database import DatabaseFactory, QueryBuilder

# データベース作成
db = DatabaseFactory.create('dynamodb', tenant_id='tenant-001')

# クエリ実行
query = QueryBuilder('users').filter('age', '>', 18).limit(10)
results = await db.query(query.build())
```

### AI呼び出し

```python
from makoto_common.ai.providers import OpenAIProvider

provider = OpenAIProvider(api_key='...')
response = await provider.generate(
    messages=[{'role': 'user', 'content': 'Hello!'}],
    model='gpt-4'
)
```

### イベント発行

```python
from makoto_common.events import UserCreatedEvent, publish_event

event = UserCreatedEvent(
    user_id='user-001',
    username='testuser',
    email='test@example.com'
)
await publish_event(event)
```

## テスト

```bash
cd tests
pytest -v --cov=makoto_common
```

## ディレクトリ構造

```
common/
├── python/
│   └── makoto_common/
│       ├── __init__.py
│       ├── types/          # 型定義
│       ├── tenant/         # テナント管理
│       ├── database/       # DB抽象化
│       ├── ai/             # AI統合
│       ├── events/         # イベント処理
│       ├── validators/     # バリデーション
│       ├── errors.py       # エラー定義
│       ├── exceptions.py   # 例外処理
│       ├── utils.py        # ユーティリティ
│       └── aws_clients.py  # AWSクライアント
├── requirements.txt
├── build.sh
├── deploy.sh
└── layer.yaml
```

## 設定

### 環境変数

- `AWS_DEFAULT_REGION`: AWSリージョン (デフォルト: ap-northeast-1)
- `ENVIRONMENT`: 実行環境 (dev/staging/prod)
- `LOG_LEVEL`: ログレベル (DEBUG/INFO/WARNING/ERROR)

### Layer設定

`layer.yaml` で詳細な設定が可能です。

## バージョニング

セマンティックバージョニングに従います。
- MAJOR: 後方互換性のない変更
- MINOR: 後方互換性のある機能追加
- PATCH: バグ修正

## ライセンス

Proprietary - MAKOTO Visual AI

## サポート

問題や質問がある場合は、GitHubのIssueを作成してください。