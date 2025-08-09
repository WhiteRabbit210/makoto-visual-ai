# Lambda Layer テスト計画書

## 目次

1. [概要](#概要)
2. [テスト戦略](#テスト戦略)
3. [テストカテゴリ](#テストカテゴリ)
4. [テスト環境](#テスト環境)
5. [テストケース一覧](#テストケース一覧)
6. [CI/CD統合](#cicd統合)
7. [カバレッジ目標](#カバレッジ目標)

## 概要

MAKOTO Visual AI Lambda Layerの品質保証のための包括的なテスト計画です。

### テスト対象

- makoto_common パッケージ全体
- 各モジュールの単体テスト
- モジュール間の統合テスト
- マルチテナント機能のセキュリティテスト

## テスト戦略

### 1. ピラミッド型テスト構造

```
         E2E Tests (5%)
        /            \
    Integration Tests (25%)
   /                    \
  Unit Tests (70%)
```

### 2. テスト原則

- **独立性**: 各テストは独立して実行可能
- **再現性**: 同じ条件で常に同じ結果
- **高速性**: ユニットテストは100ms以内
- **明確性**: テスト名から目的が明確
- **完全性**: エッジケースも網羅

## テストカテゴリ

### 1. ユニットテスト

#### 1.1 型定義モジュール
- プリミティブ型のバリデーション
- エンティティの初期化と変換
- APIレスポンスの構築

#### 1.2 テナントモジュール
- テナントコンテキストの管理
- アイソレーション機能
- リソース所有権の検証

#### 1.3 データベースモジュール
- DynamoDBアダプタの動作
- CosmosDBアダプタの動作
- ファクトリーパターンの選択ロジック

#### 1.4 AIモジュール
- プロバイダー選択
- メッセージ変換
- ストリーミング処理

### 2. 統合テスト

#### 2.1 テナント×データベース
- テナント別テーブル分離
- クロステナントアクセス拒否

#### 2.2 テナント×AI
- テナント設定に基づくプロバイダー選択
- APIキー管理

### 3. セキュリティテスト

#### 3.1 テナント分離
- 他テナントデータへのアクセス試行
- SQLインジェクション対策
- 権限昇格の防止

#### 3.2 認証・認可
- 無効なトークンの拒否
- 期限切れトークンの処理

### 4. パフォーマンステスト

#### 4.1 レスポンス時間
- API呼び出しのレイテンシ
- データベースクエリの最適化

#### 4.2 スケーラビリティ
- 同時接続数の上限
- メモリ使用量の監視

## テスト環境

### ローカル環境

```yaml
services:
  - DynamoDB Local
  - CosmosDB Emulator
  - LocalStack (AWS services)
  - Mock LLM Server
```

### CI環境

```yaml
GitHub Actions:
  - Python 3.9, 3.10, 3.11
  - Docker Compose
  - Coverage報告
  - 自動マージ条件
```

## テストケース一覧

### 重要度: Critical

| ID | モジュール | テストケース | 期待結果 |
|----|-----------|-------------|----------|
| TC001 | tenant/isolation | 他テナントリソースアクセス拒否 | PermissionError |
| TC002 | database/factory | テナント別DB選択 | 正しいアダプタ返却 |
| TC003 | ai/providers | APIキー不正時のエラー | ValueError |
| TC004 | tenant/context | コンテキスト未設定時の動作 | RuntimeError |
| TC005 | database/dynamodb | テナントIDフィルタリング | 自テナントのみ取得 |

### 重要度: High

| ID | モジュール | テストケース | 期待結果 |
|----|-----------|-------------|----------|
| TC101 | types/entities | Chat作成時のバリデーション | 正常作成 |
| TC102 | ai/interface | ストリーミング応答 | AsyncIterator動作 |
| TC103 | database/cosmosdb | バッチ書き込み | 部分失敗の処理 |
| TC104 | tenant/manager | プラン別機能制限 | 機能フラグ適用 |
| TC105 | utils | UUID生成の一意性 | 重複なし |

### 重要度: Medium

| ID | モジュール | テストケース | 期待結果 |
|----|-----------|-------------|----------|
| TC201 | types/api | ページネーション | 正しいmeta情報 |
| TC202 | ai/providers | トークンカウント | 概算値返却 |
| TC203 | database/interface | クエリビルダー | SQL生成 |
| TC204 | tenant/manager | LLM設定更新 | 設定反映 |
| TC205 | events | イベント発火 | リスナー呼び出し |

## CI/CD統合

### GitHub Actions ワークフロー

```yaml
name: Test Lambda Layer

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit --cov=makoto_common --cov-report=xml
    
    - name: Run integration tests
      run: |
        docker-compose up -d
        pytest tests/integration
        docker-compose down
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## カバレッジ目標

### 全体目標
- **ライン**: 85%以上
- **ブランチ**: 80%以上
- **関数**: 90%以上

### モジュール別目標

| モジュール | ライン | ブランチ | 関数 |
|-----------|--------|---------|------|
| types/* | 95% | 90% | 100% |
| tenant/* | 90% | 85% | 95% |
| database/* | 85% | 80% | 90% |
| ai/* | 80% | 75% | 85% |
| utils | 100% | 95% | 100% |

## テスト実行コマンド

### 全テスト実行
```bash
pytest
```

### カバレッジ付き実行
```bash
pytest --cov=makoto_common --cov-report=html
```

### 特定モジュールのみ
```bash
pytest tests/unit/test_tenant.py -v
```

### マーカー別実行
```bash
# 高速テストのみ
pytest -m "not slow"

# セキュリティテストのみ
pytest -m security
```

## モックとフィクスチャ

### 共通フィクスチャ

```python
@pytest.fixture
def tenant_context():
    """テナントコンテキストのモック"""
    return TenantContext(
        tenant_id="test-tenant",
        user_id="test-user",
        request_id="test-request",
        created_at=datetime.utcnow()
    )

@pytest.fixture
def mock_dynamodb():
    """DynamoDB Localのセットアップ"""
    # ...

@pytest.fixture
def mock_llm_response():
    """LLM応答のモック"""
    # ...
```

## テストデータ管理

### シードデータ
```yaml
# tests/fixtures/seed_data.yaml
tenants:
  - id: test-tenant-1
    name: テスト企業A
    plan: PROFESSIONAL
    
users:
  - id: test-user-1
    tenant_id: test-tenant-1
    email: test@example.com
```

## 継続的改善

### メトリクス収集
- テスト実行時間
- フレイキーテストの検出
- カバレッジ推移

### 定期レビュー
- 月次: テストカバレッジレビュー
- 四半期: テスト戦略の見直し
- 年次: テストフレームワーク更新