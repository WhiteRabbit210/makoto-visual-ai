# MAKOTO Visual AI - クラウド関数

## 概要

MAKOTO Visual AIの日次バッチ処理をAWS LambdaまたはAzure Functionsで実行するためのコードです。

## ディレクトリ構成

```
cloud_functions/
├── README.md                      # このファイル
├── deployment_guide.md            # デプロイメント概要
├── deployment_step_by_step.md    # 詳細なデプロイ手順
│
├── aws_lambda/                    # AWS Lambda用
│   ├── daily_batch.py            # Lambda関数本体
│   ├── template.yaml             # SAMテンプレート
│   └── layers/                   # Lambda Layer用ディレクトリ
│
└── azure_functions/               # Azure Functions用
    └── daily_batch/              # Timer Trigger関数
        ├── __init__.py           # Azure Functions本体
        └── function.json         # トリガー設定
```

## クイックスタート

### AWS Lambda

```bash
# SAM CLIでデプロイ
cd aws_lambda
sam build
sam deploy --guided
```

### Azure Functions

```bash
# Azure Functions Core Toolsでデプロイ
cd azure_functions
func azure functionapp publish <FunctionAppName>
```

## 機能

### 日次バッチ処理
- **実行時間**: 毎日午前2時（JST）
- **処理内容**: 前日のメッセージデータをParquet形式に変換
- **出力先**: S3/Blob Storageの分析用ディレクトリ
- **対応形式**: Athena/Synapse Analytics対応

### マルチテナント対応
- 複数テナントの並列処理
- テナントごとの独立したデータ管理
- エラー時の部分的継続

## 環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| TENANT_ID | 処理対象テナントID（カンマ区切り） | default_tenant |
| TARGET_DATE_OFFSET | 処理対象日のオフセット | -1（昨日） |

### AWS固有
- AWS_DEFAULT_REGION
- S3_BUCKET_NAME
- DYNAMODB_TABLE_NAME

### Azure固有
- AZURE_STORAGE_CONNECTION_STRING
- COSMOS_ENDPOINT
- COSMOS_KEY

## ドキュメント

1. **[デプロイメントガイド](deployment_guide.md)**
   - 概要と基本的なデプロイ方法
   - モニタリング設定
   - コスト最適化

2. **[詳細デプロイ手順](deployment_step_by_step.md)**
   - ステップバイステップの手順
   - トラブルシューティング
   - チェックリスト

## テスト実行

### ローカルテスト

```bash
# バッチ処理を手動実行
cd ../services
python batch_processor.py 2025-08-11 default_tenant
```

### AWS Lambda手動実行

```bash
aws lambda invoke \
  --function-name makoto-daily-batch-processor \
  --payload '{"target_date": "2025-08-11"}' \
  response.json
```

### Azure Functions手動実行

```bash
# ローカル
func start
curl http://localhost:7071/admin/functions/daily_batch

# Azure上
az functionapp function show \
  --name makoto-batch-processor \
  --resource-group makoto-batch-rg \
  --function-name daily_batch
```

## パフォーマンス目安

| データ量 | 処理時間 | メモリ使用量 | 推奨構成 |
|---------|----------|-------------|----------|
| 〜1,000件/日 | 〜1分 | 〜512MB | Lambda 512MB / Consumption Plan |
| 〜10,000件/日 | 〜5分 | 〜1GB | Lambda 1GB / Consumption Plan |
| 〜100,000件/日 | 〜15分 | 〜3GB | Lambda 3GB / Premium Plan |
| 100,000件/日〜 | 15分〜 | 3GB〜 | EMR/Databricks推奨 |

## コスト見積もり

### AWS Lambda
- 実行時間: 5分 × 30日 = 150分/月
- メモリ: 3GB
- **月額費用**: 約$10

### Azure Functions
- Consumption Plan: 最初の100万実行無料
- Premium Plan: 約$180/月（常時起動）
- **推奨**: 小〜中規模はConsumption Plan

## トラブルシューティング

### よくある問題

1. **タイムアウト**
   - バッチサイズを小さくする
   - 並列処理を増やす

2. **メモリ不足**
   - メモリ割り当てを増やす
   - データを分割処理

3. **権限エラー**
   - IAMロール/マネージドIDを確認
   - ストレージアクセス権限を確認

詳細は[デプロイ手順書](deployment_step_by_step.md#よくある問題と解決方法)を参照。

## サポート

問題が発生した場合は、以下を確認してください：

1. CloudWatch Logs / Application Insightsのエラーログ
2. 環境変数の設定
3. IAM/RBACの権限設定
4. ネットワーク設定（VPC/VNet）

---

**最終更新**: 2025年8月12日  
**バージョン**: 1.0.0