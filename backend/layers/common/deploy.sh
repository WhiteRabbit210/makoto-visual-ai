#!/bin/bash

# Lambda Layer デプロイスクリプト
# AWS Lambda Layerにデプロイ

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Lambda Layer デプロイを開始します...${NC}"

# 引数処理
ENVIRONMENT=${1:-dev}
REGION=${2:-ap-northeast-1}

# 変数定義
LAYER_NAME="makoto-common-layer"
LAYER_NAME_ENV="${LAYER_NAME}-${ENVIRONMENT}"
PYTHON_VERSION="python3.11"
ZIP_FILE="${LAYER_NAME}.zip"
DESCRIPTION="MAKOTO Visual AI Common Library Layer"

# 環境チェック
if ! command -v aws &> /dev/null; then
    echo -e "${RED}エラー: AWS CLIがインストールされていません${NC}"
    exit 1
fi

# ZIPファイル存在チェック
if [ ! -f ${ZIP_FILE} ]; then
    echo -e "${YELLOW}ZIPファイルが見つかりません。ビルドを実行します...${NC}"
    ./build.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}ビルドに失敗しました${NC}"
        exit 1
    fi
fi

# AWS認証チェック
echo -e "${YELLOW}AWS認証を確認...${NC}"
aws sts get-caller-identity --region ${REGION} > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}AWS認証に失敗しました。認証情報を確認してください。${NC}"
    exit 1
fi

# S3バケット名（大きなLayerの場合はS3経由でアップロード）
S3_BUCKET="makoto-lambda-layers-${ENVIRONMENT}"
S3_KEY="layers/${LAYER_NAME}/${LAYER_NAME}-$(date +%Y%m%d-%H%M%S).zip"

# ファイルサイズチェック（50MB以上はS3経由）
FILE_SIZE=$(stat -f%z ${ZIP_FILE} 2>/dev/null || stat -c%s ${ZIP_FILE})
USE_S3=false

if [ ${FILE_SIZE} -gt 52428800 ]; then
    echo -e "${YELLOW}ファイルサイズが50MBを超えているため、S3経由でアップロードします...${NC}"
    USE_S3=true
    
    # S3バケット存在チェック
    aws s3 ls s3://${S3_BUCKET} --region ${REGION} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}S3バケットを作成: ${S3_BUCKET}${NC}"
        aws s3 mb s3://${S3_BUCKET} --region ${REGION}
    fi
    
    # S3にアップロード
    echo -e "${YELLOW}S3にアップロード: s3://${S3_BUCKET}/${S3_KEY}${NC}"
    aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/${S3_KEY} --region ${REGION}
fi

# Lambda Layerを発行
echo -e "${YELLOW}Lambda Layerを発行...${NC}"

if [ "$USE_S3" = true ]; then
    RESPONSE=$(aws lambda publish-layer-version \
        --layer-name ${LAYER_NAME_ENV} \
        --description "${DESCRIPTION} (${ENVIRONMENT})" \
        --content S3Bucket=${S3_BUCKET},S3Key=${S3_KEY} \
        --compatible-runtimes ${PYTHON_VERSION} \
        --region ${REGION} \
        --output json)
else
    RESPONSE=$(aws lambda publish-layer-version \
        --layer-name ${LAYER_NAME_ENV} \
        --description "${DESCRIPTION} (${ENVIRONMENT})" \
        --zip-file fileb://${ZIP_FILE} \
        --compatible-runtimes ${PYTHON_VERSION} \
        --region ${REGION} \
        --output json)
fi

# レスポンスから情報を抽出
LAYER_VERSION_ARN=$(echo $RESPONSE | jq -r '.LayerVersionArn')
LAYER_VERSION=$(echo $RESPONSE | jq -r '.Version')

echo -e "${GREEN}デプロイ完了！${NC}"
echo ""
echo -e "${BLUE}Layer情報:${NC}"
echo "  Layer名: ${LAYER_NAME_ENV}"
echo "  バージョン: ${LAYER_VERSION}"
echo "  ARN: ${LAYER_VERSION_ARN}"
echo ""

# パーミッション設定（オプション）
echo -e "${YELLOW}Layerのパーミッションを設定しますか？ (y/n)${NC}"
read -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}組織全体にLayerを公開...${NC}"
    aws lambda add-layer-version-permission \
        --layer-name ${LAYER_NAME_ENV} \
        --version-number ${LAYER_VERSION} \
        --statement-id allow-org-access \
        --principal '*' \
        --action lambda:GetLayerVersion \
        --region ${REGION} > /dev/null 2>&1 || true
    echo -e "${GREEN}パーミッション設定完了${NC}"
fi

# Layer設定ファイルを更新
echo -e "${YELLOW}Layer設定ファイルを更新...${NC}"
cat > layer-config.json <<EOF
{
  "environment": "${ENVIRONMENT}",
  "region": "${REGION}",
  "layer_name": "${LAYER_NAME_ENV}",
  "layer_version": ${LAYER_VERSION},
  "layer_arn": "${LAYER_VERSION_ARN}",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo -e "${GREEN}設定ファイルを layer-config.json に保存しました${NC}"

# クリーンアップ（S3）
if [ "$USE_S3" = true ]; then
    echo -e "${YELLOW}S3のファイルを削除しますか？ (y/n)${NC}"
    read -r REPLY
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        aws s3 rm s3://${S3_BUCKET}/${S3_KEY} --region ${REGION}
        echo -e "${GREEN}S3ファイルを削除しました${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Lambda Layerのデプロイが完了しました！${NC}"
echo ""
echo "Lambda関数でこのLayerを使用するには:"
echo "  1. Lambda関数の設定でLayerを追加"
echo "  2. ARNを指定: ${LAYER_VERSION_ARN}"
echo "  3. コードで使用: from makoto_common import ..."