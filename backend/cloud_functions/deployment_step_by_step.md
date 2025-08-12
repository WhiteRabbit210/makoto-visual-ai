# 日次バッチ処理 デプロイ手順書

## 目次
1. [事前準備](#事前準備)
2. [AWS Lambda デプロイ詳細手順](#aws-lambda-デプロイ詳細手順)
3. [Azure Functions デプロイ詳細手順](#azure-functions-デプロイ詳細手順)
4. [デプロイ後の確認](#デプロイ後の確認)
5. [よくある問題と解決方法](#よくある問題と解決方法)

## 事前準備

### 必要なツール

#### AWS用
```bash
# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# SAM CLI
pip install aws-sam-cli

# AWS認証設定
aws configure
# Access Key ID: YOUR_ACCESS_KEY
# Secret Access Key: YOUR_SECRET_KEY
# Default region: ap-northeast-1
# Default output format: json
```

#### Azure用
```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Azureログイン
az login

# サブスクリプション設定
az account set --subscription "YOUR_SUBSCRIPTION_ID"
```

### 依存ライブラリの準備

```bash
# プロジェクトディレクトリに移動
cd /home/whiterabbit/Projects/makoto_ui-1/makoto/backend

# Python仮想環境作成
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 必要なライブラリインストール
pip install pandas pyarrow boto3 azure-storage-blob azure-cosmos
```

## AWS Lambda デプロイ詳細手順

### 方法1: SAM CLIを使用（推奨）

#### Step 1: 依存関係の準備
```bash
cd cloud_functions/aws_lambda

# Layerディレクトリ作成
mkdir -p layers/python/lib/python3.11/site-packages

# 依存ライブラリをLayer用にインストール
pip install pandas pyarrow boto3 -t layers/python/lib/python3.11/site-packages/

# サービスコードをコピー
cp -r ../../services layers/python/lib/python3.11/site-packages/
```

#### Step 2: SAMテンプレートの修正
```bash
# template.yamlのパラメータを環境に合わせて修正
vim template.yaml

# 主な修正箇所：
# - S3BucketName: your-actual-bucket-name
# - TenantId: your-tenant-ids (カンマ区切り)
```

#### Step 3: ビルドとデプロイ
```bash
# ビルド
sam build

# 初回デプロイ（対話形式）
sam deploy --guided

# 以下の質問に回答：
# Stack Name [sam-app]: makoto-batch-processor
# AWS Region [ap-northeast-1]: ap-northeast-1
# Parameter S3BucketName []: your-bucket-name
# Parameter TenantId [default_tenant]: your-tenant-id
# Confirm changes before deploy [y/N]: y
# Allow SAM CLI IAM role creation [Y/n]: Y
# Save arguments to configuration file [Y/n]: Y
# SAM configuration file [samconfig.toml]: samconfig.toml

# 2回目以降のデプロイ
sam deploy
```

### 方法2: AWS Console経由

#### Step 1: Lambda関数作成
1. AWS Consoleにログイン
2. Lambda → 「関数の作成」
3. 設定：
   - 関数名: `makoto-daily-batch-processor`
   - ランタイム: Python 3.11
   - アーキテクチャ: x86_64
   - 実行ロール: 新しいロールを作成

#### Step 2: コードのアップロード
```bash
# デプロイパッケージ作成
cd cloud_functions/aws_lambda
mkdir package
pip install pandas pyarrow boto3 -t package/
cp -r ../../services package/
cp daily_batch.py package/
cd package
zip -r ../function.zip .
cd ..

# AWS CLIでアップロード
aws lambda update-function-code \
  --function-name makoto-daily-batch-processor \
  --zip-file fileb://function.zip
```

#### Step 3: 環境変数設定
```bash
aws lambda update-function-configuration \
  --function-name makoto-daily-batch-processor \
  --environment "Variables={TENANT_ID=default_tenant,TARGET_DATE_OFFSET=-1,S3_BUCKET_NAME=your-bucket}" \
  --timeout 900 \
  --memory-size 3008
```

#### Step 4: EventBridgeルール作成
```bash
# ルール作成
aws events put-rule \
  --name makoto-daily-batch-schedule \
  --schedule-expression "cron(0 17 * * ? *)" \
  --description "毎日午前2時（JST）にバッチ処理実行"

# Lambda関数の権限追加
aws lambda add-permission \
  --function-name makoto-daily-batch-processor \
  --statement-id makoto-batch-schedule-permission \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:ap-northeast-1:YOUR_ACCOUNT:rule/makoto-daily-batch-schedule

# ターゲット追加
aws events put-targets \
  --rule makoto-daily-batch-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:ap-northeast-1:YOUR_ACCOUNT:function:makoto-daily-batch-processor"
```

#### Step 5: IAMロール権限追加
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
        "arn:aws:s3:::your-bucket/*",
        "arn:aws:s3:::your-bucket"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/makoto-metadata"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Azure Functions デプロイ詳細手順

### 方法1: Azure Functions Core Tools使用（推奨）

#### Step 1: Function App作成
```bash
# リソースグループ作成
az group create --name makoto-batch-rg --location japaneast

# ストレージアカウント作成
az storage account create \
  --name makotobatchstorage \
  --location japaneast \
  --resource-group makoto-batch-rg \
  --sku Standard_LRS

# Function App作成
az functionapp create \
  --resource-group makoto-batch-rg \
  --consumption-plan-location japaneast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name makoto-batch-processor \
  --storage-account makotobatchstorage
```

#### Step 2: プロジェクト準備
```bash
cd cloud_functions/azure_functions

# プロジェクト初期化
func init --python

# requirements.txt作成
cat > requirements.txt << EOF
azure-functions
pandas
pyarrow
azure-storage-blob
azure-cosmos
EOF

# host.json作成
cat > host.json << EOF
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
EOF

# サービスコードをコピー
cp -r ../../services .
```

#### Step 3: ローカルテスト
```bash
# ローカル実行
func start

# 別ターミナルで手動トリガー
curl http://localhost:7071/admin/functions/daily_batch
```

#### Step 4: デプロイ
```bash
# Azureへデプロイ
func azure functionapp publish makoto-batch-processor --python

# 環境変数設定
az functionapp config appsettings set \
  --name makoto-batch-processor \
  --resource-group makoto-batch-rg \
  --settings \
    TENANT_ID=default_tenant \
    TARGET_DATE_OFFSET=-1 \
    AZURE_STORAGE_CONNECTION_STRING="your-connection-string" \
    COSMOS_ENDPOINT="https://your-cosmos.documents.azure.com:443/" \
    COSMOS_KEY="your-cosmos-key"
```

### 方法2: VS Code経由

#### Step 1: 拡張機能インストール
1. VS Codeを開く
2. 拡張機能で「Azure Functions」を検索してインストール
3. Azureアカウントにサインイン（F1 → "Azure: Sign In"）

#### Step 2: Function App作成
1. Azureアイコンをクリック
2. Functions → "Create Function App in Azure"
3. 設定入力：
   - 名前: makoto-batch-processor
   - ランタイム: Python 3.11
   - リージョン: Japan East

#### Step 3: デプロイ
1. F1 → "Azure Functions: Deploy to Function App"
2. フォルダ選択: `cloud_functions/azure_functions`
3. Function App選択: makoto-batch-processor
4. デプロイ確認: Deploy

#### Step 4: 環境変数設定（Portal経由）
1. Azure Portalにログイン
2. Function App → makoto-batch-processor
3. 構成 → アプリケーション設定
4. 新しいアプリケーション設定：
   - TENANT_ID: default_tenant
   - TARGET_DATE_OFFSET: -1
   - その他必要な設定

## デプロイ後の確認

### AWS Lambda

#### 関数の確認
```bash
# 関数情報取得
aws lambda get-function --function-name makoto-daily-batch-processor

# 手動実行テスト
aws lambda invoke \
  --function-name makoto-daily-batch-processor \
  --payload '{"target_date": "2025-08-11"}' \
  response.json

# ログ確認
aws logs tail /aws/lambda/makoto-daily-batch-processor --follow
```

#### CloudWatchメトリクス確認
```bash
# 実行回数
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=makoto-daily-batch-processor \
  --start-time 2025-08-11T00:00:00Z \
  --end-time 2025-08-12T00:00:00Z \
  --period 86400 \
  --statistics Sum
```

### Azure Functions

#### 関数の確認
```bash
# 関数情報取得
az functionapp show --name makoto-batch-processor --resource-group makoto-batch-rg

# 手動実行テスト
az functionapp function show \
  --name makoto-batch-processor \
  --resource-group makoto-batch-rg \
  --function-name daily_batch

# ログストリーミング
az webapp log tail --name makoto-batch-processor --resource-group makoto-batch-rg
```

#### Application Insights確認
```bash
# メトリクス取得
az monitor metrics list \
  --resource /subscriptions/YOUR_SUB/resourceGroups/makoto-batch-rg/providers/Microsoft.Web/sites/makoto-batch-processor \
  --metric requests/count \
  --interval PT1H
```

## よくある問題と解決方法

### 問題1: Lambda関数がタイムアウト

**エラー**: Task timed out after 900.00 seconds

**解決方法**:
```bash
# バッチサイズを小さくする
aws lambda update-function-configuration \
  --function-name makoto-daily-batch-processor \
  --environment "Variables={BATCH_SIZE=500}"
```

### 問題2: メモリ不足

**エラー**: MemoryError または Runtime exited with error: signal: killed

**解決方法**:
```bash
# AWS: メモリ増加
aws lambda update-function-configuration \
  --function-name makoto-daily-batch-processor \
  --memory-size 10240  # 10GB

# Azure: Premium Planへ変更
az functionapp plan create \
  --name makoto-premium-plan \
  --resource-group makoto-batch-rg \
  --sku EP1 \
  --is-linux

az functionapp update \
  --name makoto-batch-processor \
  --resource-group makoto-batch-rg \
  --plan makoto-premium-plan
```

### 問題3: 権限エラー

**エラー**: Access Denied

**解決方法**:

AWS:
```bash
# ロールに権限追加
aws iam attach-role-policy \
  --role-name makoto-batch-processor-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name makoto-batch-processor-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
```

Azure:
```bash
# マネージドIDを有効化
az webapp identity assign \
  --name makoto-batch-processor \
  --resource-group makoto-batch-rg

# ストレージへのアクセス権付与
az role assignment create \
  --assignee YOUR_MANAGED_IDENTITY_ID \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/YOUR_SUB/resourceGroups/makoto-batch-rg
```

### 問題4: パッケージサイズ超過

**エラー**: Deployment package is too large

**解決方法**:
```bash
# 不要ファイル削除
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete
find . -name "*.dist-info" -exec rm -r {} +

# 圧縮最適化
zip -r -9 function.zip . -x "*.git*" "tests/*" "*.md"
```

## デプロイチェックリスト

### AWS Lambda
- [ ] IAMロールの作成と権限設定
- [ ] S3バケットの作成とアクセス権限
- [ ] DynamoDBテーブルの作成
- [ ] Lambda関数のデプロイ
- [ ] 環境変数の設定
- [ ] EventBridgeルールの作成
- [ ] CloudWatchアラームの設定
- [ ] 手動実行テスト完了
- [ ] ログ出力確認

### Azure Functions
- [ ] リソースグループ作成
- [ ] Function App作成
- [ ] ストレージアカウント作成
- [ ] Cosmos DBアカウント作成
- [ ] 関数のデプロイ
- [ ] アプリケーション設定
- [ ] Timer Trigger設定確認
- [ ] Application Insights設定
- [ ] 手動実行テスト完了
- [ ] ログ出力確認

## サポート情報

### ログの見方

#### AWS CloudWatch Logs
```
START RequestId: xxx Version: $LATEST
[INFO] 2025-08-12 02:00:00 - Lambda開始
[INFO] 2025-08-12 02:00:01 - 処理対象日: 2025-08-11
[INFO] 2025-08-12 02:00:02 - テナント default_tenant の処理開始
[INFO] 2025-08-12 02:05:00 - 1000件のメッセージを処理
[INFO] 2025-08-12 02:05:30 - Parquetファイル保存完了
END RequestId: xxx
REPORT RequestId: xxx Duration: 330000 ms Billed Duration: 330000 ms Memory Size: 3008 MB Max Memory Used: 2500 MB
```

#### Azure Application Insights
```
2025-08-12T02:00:00 [Information] 日次バッチ処理開始
2025-08-12T02:00:01 [Information] 処理対象日: 2025-08-11
2025-08-12T02:00:02 [Information] テナント default_tenant の処理開始
2025-08-12T02:05:00 [Information] 1000件のメッセージを処理
2025-08-12T02:05:30 [Information] 出力: default_tenant/analytics/messages/year=2025/month=08/day=11/messages_20250811.parquet
2025-08-12T02:05:31 [Information] 処理完了: バッチ処理完了: 成功=1, エラー=0
```

---

**作成者**: Claude  
**作成日**: 2025年8月12日  
**バージョン**: 1.0.0