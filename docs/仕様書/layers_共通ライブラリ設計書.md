# layers 共通ライブラリ設計書

## 目次

1. [概要](#概要)
2. [ライブラリ構成とモジュール設計](#ライブラリ構成とモジュール設計)
3. [Lambda Layer配布戦略](#lambda-layer配布戦略)
4. [他プロジェクトでの流用](#他プロジェクトでの流用)
5. [型定義の管理方針](#型定義の管理方針)
6. [実装詳細](#実装詳細)
7. [運用・保守](#運用・保守)

## 概要

### プロジェクト概要

makoto_commonライブラリは、MAKOTOシステム全体で共通利用する機能を提供するPython共通ライブラリです。Lambda Layer形式で配布され、各Lambda関数で重複するロジックを排除し、コードの再利用性と保守性を向上させます。

### アーキテクチャ方針

- **型安全性**: 曖昧な型（Dict[str, Any]等）の使用を避け、dataclassによる明確な型定義を提供
- **抽象化**: データベースやAIサービスの実装詳細を隠蔽し、統一されたインターフェースを提供
- **マルチテナント対応**: テナントごとの設定とデータ分離をサポート
- **拡張性**: 新しいプロバイダーやサービスの追加に対応可能な設計

## ライブラリ構成とモジュール設計

### 全体構造

```
makoto_common/
├── __init__.py           # エントリーポイント
├── types.py              # 共通型定義
├── utils.py              # ユーティリティ関数
├── aws_clients.py        # AWSクライアント管理
├── message_handler.py    # 大容量メッセージ処理
├── ai/                   # AI応答標準化
├── database/            # データベース抽象化
├── tenant/              # マルチテナント機能
└── websocket/           # WebSocket通信（廃止予定）
```

### 1. AI応答標準化（ai/）

#### 機能概要
Function Callingとストリーミング対応のAIクライアントを提供します。

#### 主要モジュール
- **models.py**: Pydantic型定義（BotResponse、EmotionType等）
- **client.py**: AIクライアントの基底クラス
- **openai_client.py**: OpenAI/Azure OpenAI実装
- **streaming.py**: ストリーミング応答解析

#### 型定義例
```python
@dataclass
class StreamingChunk:
    """ストリーミングレスポンスの1チャンク"""
    type: ChunkType
    value: Any
    timestamp: int = None

class BotResponse(BaseModel):
    """AI応答の構造化データ"""
    content: str
    emotion: EmotionType
    category: CategoryType
    memory: Optional[str] = None
```

#### 特徴
- OpenAI/Azure OpenAIの統一インターフェース
- Function Calling対応
- ストリーミング応答のリアルタイム解析
- エラーハンドリング（レート制限、認証エラー）

### 2. データベース抽象化レイヤー（database/）

#### 機能概要
DynamoDB、CosmosDBなど異なるデータベースバックエンドを統一インターフェースで操作できます。

#### 主要モジュール
- **interface.py**: データベース操作の基本インターフェース
- **factory.py**: データベースアダプターとリポジトリのファクトリー
- **models.py**: データモデル定義
- **repositories.py**: リポジトリ抽象クラス
- **dynamodb_impl.py / cosmosdb_impl.py**: 具象実装
- **dynamodb_repositories.py / cosmosdb_repositories.py**: リポジトリ実装

#### アーキテクチャ
```
Application Layer
    ↓
Repository Layer (ChatRepository, UserRepository, etc.)
    ↓
Database Interface Layer
    ↓
Concrete Implementation (DynamoDB, CosmosDB)
```

#### 型定義例
```python
@dataclass
class MemoryItem:
    """メモリアイテム"""
    user_id: str
    memory_id: str
    content: str
    category: str
    created_at: int
    updated_at: int
```

### 3. マルチテナント機能（tenant/）

#### 機能概要
テナント識別、認証、データアクセス制御を統合管理します。

#### 主要モジュール
- **models.py**: テナント関連データモデル
- **manager.py**: テナント管理クラス
- **context.py**: テナントコンテキスト管理
- **decorators.py**: テナント認識デコレーター
- **repositories.py**: テナント認識リポジトリ

#### 型定義例
```python
@dataclass
class TenantConfig:
    """テナント設定情報"""
    tenant_id: str
    tenant_name: str
    domain: str
    cognito_user_pool_id: str
    database: TenantDatabase
    tier: TenantTier
    limits: TenantLimits

@dataclass
class TenantContext:
    """リクエスト処理中のテナントコンテキスト"""
    tenant_id: str
    config: TenantConfig
    user_id: Optional[str] = None
```

#### 特徴
- サブドメインベースのテナント識別
- ティア別の機能制限
- テナント別データベースパーティション
- キャッシュ機能付きテナント設定管理

### 4. 共通型定義（types.py）

#### 機能概要
システム全体で使用する型定義を一元管理します。

#### 主要型定義
- **Lambda Event型**: APIGatewayEvent、WebSocketEvent等
- **チャットサービス型**: ChatRequest、ChatMessage、ChatResponse
- **類似度検索型**: SimilarityRequest、VectorData等
- **音声認識型**: SpeechRequest、SpeechResponse
- **WebSocket通信型**: WebSocketMessage、WebSocketResponse

### 5. ユーティリティ（utils.py、message_handler.py等）

#### utils.py
```python
def create_response(status_code: int, body: dict) -> LambdaResponse
def parse_json_body(body: str) -> dict
def extract_user_from_jwt(authorization_header: str, user_pool_id: str) -> AuthenticatedUser
def get_cached_jwks(user_pool_id: str) -> JWKS
```

#### message_handler.py
WebSocket APIの128KB制限を回避するため、10KB以上のメッセージをS3経由で処理します。

```python
class LargeMessageHandler:
    def should_use_s3(self, message: str) -> bool
    def store_large_message(self, message: str, user_id: str, session_id: str) -> S3MessageReference
    def retrieve_large_message(self, s3_key: str) -> str
```

#### aws_clients.py
AWSサービスクライアントの初期化と管理を行います。

```python
class AWSClientManager:
    @property
    def dynamodb(self) -> boto3.resource
    @property
    def s3(self) -> boto3.client
    def get_dynamodb_table(self, table_name: str) -> boto3.dynamodb.Table
```

### 6. WebSocketモジュール（websocket/）【廃止予定】

#### 現状
WebSocket通信機能を提供していますが、アーキテクチャの簡素化により廃止予定です。

#### 廃止理由
- 複雑性の増加
- 保守コストの高さ
- 現在の要件では不要

## Lambda Layer配布戦略

### CI/CDパイプライン設計

#### GitHub Actions推奨設定

```yaml
name: Deploy Lambda Layer

on:
  push:
    branches: [main]
    paths: ['layers/common/**']
  pull_request:
    branches: [main]
    paths: ['layers/common/**']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd layers/common/python
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd layers/common/python
          pytest --cov=makoto_common tests/
      - name: Lint check
        run: |
          cd layers/common/python
          flake8 makoto_common/
          mypy makoto_common/

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        environment: [dev, staging, prod]
    steps:
      - uses: actions/checkout@v3
      - name: Setup AWS CLI
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-1
      - name: Build and Deploy Layer
        run: |
          cd layers/common
          zip -r makoto-common-layer.zip python/
          aws lambda publish-layer-version \
            --layer-name "makoto-common-${{ matrix.environment }}" \
            --zip-file fileb://makoto-common-layer.zip \
            --compatible-runtimes python3.11 \
            --description "MAKOTO Common Library v${{ github.sha }}"
```

### ビルド・テスト・配布プロセス

#### 1. ビルドプロセス
```bash
# 依存関係インストール
cd layers/common/python
pip install -r requirements.txt -t .

# Lambda Layer用ZIP作成
cd ..
zip -r makoto-common-layer.zip python/
```

#### 2. テストプロセス
```bash
# 単体テスト
pytest tests/ --cov=makoto_common

# 型チェック
mypy makoto_common/

# Lintチェック
flake8 makoto_common/
```

#### 3. 配布プロセス
- 環境別Layer作成（dev/staging/prod）
- バージョン管理とタグ付け
- Lambda関数への自動適用

### バージョン管理戦略（Semantic Versioning）

#### バージョニング規則
- **MAJOR**: 破壊的変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: 後方互換性のあるバグ修正

#### リリース戦略
```
v1.0.0: 初期リリース
v1.1.0: 新機能追加（AI応答モデル追加等）
v1.1.1: バグ修正
v2.0.0: 破壊的変更（interface変更等）
```

### 複数環境対応

#### 環境別設定
```python
# 環境変数による設定切り替え
ENVIRONMENT = dev|staging|prod
DATABASE_TYPE = dynamodb|cosmosdb
LAYER_VERSION = 1.2.3
```

#### 環境別リソース
- dev: `makoto-common-dev`
- staging: `makoto-common-staging`  
- prod: `makoto-common-prod`

## 他プロジェクトでの流用

### 汎用性のある部分の特定

#### 高い汎用性
- **types.py**: 基本的な型定義
- **utils.py**: JWT認証、レスポンス作成等
- **aws_clients.py**: AWSクライアント管理
- **database/interface.py**: データベース抽象化インターフェース

#### 中程度の汎用性
- **ai/**: AIサービスの抽象化（プロンプトの調整が必要）
- **message_handler.py**: 大容量メッセージ処理（S3設定の調整が必要）

#### 低い汎用性
- **tenant/**: MAKOTO固有のマルチテナント機能
- **database/models.py**: MAKOTO固有のデータモデル

### 依存関係の管理方針

#### 必須依存関係
```python
# requirements.txt
boto3>=1.28.0
botocore>=1.31.0
pydantic>=2.0.0
python-jose>=3.3.0
requests>=2.31.0
```

#### オプション依存関係
```python
# requirements-optional.txt
azure-cosmos>=4.3.0  # CosmosDB使用時
openai>=1.0.0        # OpenAI使用時
```

### ドキュメント・サンプルコード提供

#### 利用ガイド作成
```markdown
# makoto_common利用ガイド

## インストール
```bash
# Lambda Layer追加
aws lambda update-function-configuration \
  --function-name your-function \
  --layers arn:aws:lambda:region:account:layer:makoto-common:version
```

## 基本的な使用方法
```python
from makoto_common import create_response, parse_json_body
from makoto_common.ai import get_ai_client
from makoto_common.database import create_repositories

def lambda_handler(event, context):
    # JSON解析
    data = parse_json_body(event['body'])
    
    # AI応答生成
    ai_client = get_ai_client()
    response = await ai_client.chat_completion_stream(messages, user_id, session_id)
    
    # レスポンス返却
    return create_response(200, {"message": "成功"})
```

#### プロジェクトテンプレート提供
```
project-template/
├── lambda_function.py     # エントリーポイント例
├── requirements.txt       # 依存関係
├── serverless.yml        # Serverless Framework設定例
└── terraform/            # Terraform設定例
    ├── main.tf
    └── variables.tf
```

## 型定義の管理方針

### Python dataclass ↔ TypeScript interface 対応

#### 自動生成ツール検討
```python
# generate_types.py
from makoto_common.types import *
import json

def generate_typescript_interfaces():
    """Python dataclassからTypeScript interfaceを生成"""
    # 実装検討中
```

#### 手動管理による対応
```typescript
// types.ts
export interface ChatRequest {
  user_id: string;
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  user_id: string;
  session_id: string;
}
```

### APIレスポンス型の統一

#### 共通レスポンス型
```python
@dataclass
class APIResponse:
    """API共通レスポンス"""
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: int = field(default_factory=get_current_timestamp)
```

#### エラーレスポンス統一
```python
@dataclass
class ErrorResponse:
    """エラーレスポンス"""
    error: str
    error_code: str
    timestamp: int
    request_id: Optional[str] = None
```

### バリデーション統合

#### Pydanticによるバリデーション
```python
class ChatRequestValidator(BaseModel):
    """チャットリクエストバリデーター"""
    message: str = Field(min_length=1, max_length=1000)
    session_id: str = Field(pattern=r'^[a-f0-9-]{36}$')
    
    @validator('message')
    def sanitize_message(cls, v):
        return sanitize_user_input(v)
```

## 実装詳細

### 主要クラス設計

#### TenantManager
```python
class TenantManager:
    """テナント管理クラス"""
    
    def __init__(self, table_name: str, db_adapter: DatabaseInterface):
        self.table_name = table_name
        self._db_adapter = db_adapter
        self._cache: Dict[str, TenantConfig] = {}
    
    async def get_tenant_config(self, tenant_id: str) -> Optional[TenantConfig]:
        """テナント設定取得（キャッシュ対応）"""
        
    def extract_tenant_id(self, host: str) -> str:
        """ホスト名からテナントID抽出"""
```

#### AIClient基底クラス
```python
class AIClient(ABC):
    """AI クライアント基底クラス"""
    
    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        user_id: str,
        session_id: str
    ) -> AsyncIterator[StreamingChunk]:
        """ストリーミングチャット応答"""
```

### セキュリティ設計

#### JWT認証
```python
def extract_user_from_jwt(authorization_header: str, user_pool_id: str) -> AuthenticatedUser:
    """JWT トークンからユーザー情報抽出"""
    # JWKS キャッシュ機能
    # トークン検証
    # ユーザー情報抽出
```

#### 入力サニタイゼーション
```python
def sanitize_user_input(input_text: str, max_length: int = 1000) -> str:
    """ユーザー入力サニタイゼーション"""
    # 文字数制限
    # 基本的なサニタイズ
```

### パフォーマンス最適化

#### キャッシュ戦略
- JWKS: DynamoDB + 24時間TTL
- テナント設定: メモリ + 5分TTL
- データベース接続: 接続プール

#### バッチ処理
```python
async def batch_write_items(self, table_name: str, items: List[Dict[str, Any]]) -> None:
    """バッチ書き込み（25件ずつ）"""
```

## 運用・保守

### モニタリング

#### ログ出力
```python
import logging
logger = logging.getLogger(__name__)

def log_error(operation: str, error: Exception, context: dict):
    """統一エラーログ"""
    logger.error(f"Operation: {operation}, Error: {str(error)}", extra=context)
```

#### メトリクス収集
- API呼び出し数
- エラー率
- レスポンス時間
- テナント別使用量

### アラート設定

#### CloudWatch Alarms
- Lambda エラー率 > 5%
- DynamoDB スロットリング
- Layer サイズ制限超過

### トラブルシューティング

#### 一般的な問題と対策

1. **Import エラー**
   - Layer バージョン確認
   - 依存関係チェック

2. **認証エラー**
   - JWT トークン形式確認
   - JWKS キャッシュ更新

3. **データベース接続エラー**
   - テーブル存在確認
   - IAM 権限確認

### 更新・アップグレード手順

#### マイナーアップデート
1. テスト実行
2. Layer 新バージョン発行
3. 段階的デプロイ（dev → staging → prod）

#### メジャーアップデート
1. 互換性影響調査
2. 移行計画作成
3. バックアップ取得
4. 段階的移行実施
5. 検証・ロールバック準備

### バックアップ・リストア

#### Layer バージョン管理
- 過去バージョンの保持（最新10バージョン）
- 緊急時のロールバック手順

#### 設定バックアップ
- テナント設定の定期バックアップ
- 災害復旧手順

---

**作成者**: Claude  
**作成日**: 2025年8月7日  
**バージョン**: 1.0.0