# クラウド関数デプロイメントガイド

## 目次
1. [概要](#概要)
2. [AWS Lambda](#aws-lambda)
3. [Azure Functions](#azure-functions)
4. [環境変数設定](#環境変数設定)
5. [モニタリング](#モニタリング)

## 概要

MAKOTO Visual AIの日次バッチ処理をAWSとAzure両方で実行できるようにしています。
毎日午前2時に前日のメッセージデータをParquet形式に変換し、分析用ストレージに保存します。

## AWS Lambda

### デプロイ手順

#### 1. SAM CLIを使用する場合

```bash
# SAM CLIのインストール
pip install aws-sam-cli

# ディレクトリ移動
cd /makoto/backend/cloud_functions/aws_lambda

# 依存関係のインストール（Layer用）
mkdir -p layers/python
pip install pandas pyarrow boto3 -t layers/python/

# ビルド
sam build

# デプロイ（初回）
sam deploy --guided

# デプロイ（2回目以降）
sam deploy
```

#### 2. AWS Consoleから直接デプロイ

1. Lambda関数を作成
   - ランタイム: Python 3.11
   - メモリ: 3008 MB
   - タイムアウト: 15分

2. コードをアップロード
   ```bash
   zip -r function.zip daily_batch.py
   aws lambda update-function-code --function-name makoto-daily-batch-processor --zip-file fileb://function.zip
   ```

3. EventBridgeルールを作成
   - スケジュール式: `cron(0 17 * * ? *)`（UTC 17:00 = JST 2:00）

### 必要なIAMポリシー

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/*",
        "arn:aws:s3:::your-bucket-name"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:GetItem",
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/makoto-metadata"
    }
  ]
}
```

## Azure Functions

### デプロイ手順

#### 1. Azure Functions Core Toolsを使用

```bash
# Azure Functions Core Toolsのインストール
npm install -g azure-functions-core-tools@4

# ディレクトリ移動
cd /makoto/backend/cloud_functions/azure_functions

# 初期化
func init --python

# ローカルテスト
func start

# Azureへデプロイ
func azure functionapp publish <FunctionAppName>
```

#### 2. VS Code拡張機能を使用

1. Azure Functions拡張機能をインストール
2. F1 → "Azure Functions: Deploy to Function App"
3. サブスクリプションとFunction Appを選択

### 必要な設定

#### host.json
```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
```

#### requirements.txt
```txt
azure-functions
pandas
pyarrow
azure-storage-blob
azure-cosmos
```

## 環境変数設定

### 共通環境変数

| 変数名 | 説明 | デフォルト値 |
|--------|------|------------|
| TENANT_ID | 処理対象テナントID（カンマ区切り） | default_tenant |
| TARGET_DATE_OFFSET | 処理対象日オフセット | -1（昨日） |

### AWS固有

| 変数名 | 説明 |
|--------|------|
| AWS_DEFAULT_REGION | AWSリージョン |
| S3_BUCKET_NAME | S3バケット名 |
| DYNAMODB_TABLE_NAME | DynamoDBテーブル名 |

### Azure固有

| 変数名 | 説明 |
|--------|------|
| AZURE_STORAGE_CONNECTION_STRING | Blob Storage接続文字列 |
| COSMOS_ENDPOINT | Cosmos DBエンドポイント |
| COSMOS_KEY | Cosmos DBキー |

## モニタリング

### AWS CloudWatch

#### メトリクス
- Invocations: 実行回数
- Duration: 実行時間
- Errors: エラー数
- Throttles: スロットリング数

#### ログ
```bash
# ログを確認
aws logs tail /aws/lambda/makoto-daily-batch-processor --follow
```

#### アラーム設定
```bash
aws cloudwatch put-metric-alarm \
  --alarm-name makoto-batch-failure \
  --alarm-description "バッチ処理失敗" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 86400 \
  --evaluation-periods 1 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold
```

### Azure Application Insights

#### クエリ例
```kusto
// 過去24時間のバッチ処理結果
traces
| where timestamp > ago(24h)
| where cloud_RoleName == "makoto-daily-batch"
| where severityLevel >= 3  // エラーレベル以上
| project timestamp, message, severityLevel
| order by timestamp desc

// 処理時間の統計
requests
| where timestamp > ago(7d)
| where cloud_RoleName == "makoto-daily-batch"
| summarize 
    avg_duration = avg(duration),
    max_duration = max(duration),
    min_duration = min(duration),
    count = count()
  by bin(timestamp, 1d)
```

## トラブルシューティング

### 問題: メモリ不足

**症状**: `MemoryError`または関数のタイムアウト

**解決策**:
- AWS: メモリを3008MB以上に増やす
- Azure: Premium Planにアップグレード

### 問題: タイムアウト

**症状**: 15分以上かかって処理が中断

**解決策**:
1. バッチサイズを小さくする（batch_processor.pyの`batch_size`を調整）
2. 並列処理を導入
3. Step Functionsや Logic Appsでワークフロー化

### 問題: 権限エラー

**症状**: `AccessDenied`エラー

**解決策**:
- IAMロール/マネージドIDの権限を確認
- ストレージのアクセスポリシーを確認

## コスト最適化

### AWS
- Lambda: 月100万リクエストまで無料枠
- 実行時間: 3GB × 15分 × 30日 = 約$10/月

### Azure
- Consumption Plan: 月100万実行まで無料
- Premium Plan: 約$180/月（常時起動）

### 推奨設定
- 小規模（〜1000メッセージ/日）: Consumption/無料枠で十分
- 中規模（〜10万メッセージ/日）: Lambda 3GB or Azure Premium
- 大規模（10万メッセージ/日〜）: EMRやDatabricksを検討

---

**作成者**: Claude  
**作成日**: 2025年8月12日  
**バージョン**: 1.0.0