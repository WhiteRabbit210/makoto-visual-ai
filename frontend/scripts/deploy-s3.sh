#!/bin/bash

# S3デプロイスクリプト
# 使用方法: ./scripts/deploy-s3.sh [環境名]

set -e

# デフォルト環境は production
ENVIRONMENT=${1:-production}

# 環境ごとの設定
if [ "$ENVIRONMENT" == "production" ]; then
    S3_BUCKET="makoto-frontend-prod"
    CLOUDFRONT_DISTRIBUTION_ID="E1234567890ABC"
    AWS_PROFILE="makoto-prod"
elif [ "$ENVIRONMENT" == "staging" ]; then
    S3_BUCKET="makoto-frontend-staging"
    CLOUDFRONT_DISTRIBUTION_ID="E0987654321XYZ"
    AWS_PROFILE="makoto-staging"
else
    echo "不明な環境: $ENVIRONMENT"
    echo "使用方法: ./scripts/deploy-s3.sh [production|staging]"
    exit 1
fi

echo "================================"
echo "環境: $ENVIRONMENT"
echo "S3バケット: $S3_BUCKET"
echo "CloudFront: $CLOUDFRONT_DISTRIBUTION_ID"
echo "================================"

# ビルド
echo "ビルドを開始します..."
npm run build

# S3へのアップロード
echo "S3へアップロードします..."
aws s3 sync dist/ s3://$S3_BUCKET/ \
    --delete \
    --profile $AWS_PROFILE \
    --region ap-northeast-1 \
    --exclude ".git/*" \
    --exclude ".env*" \
    --exclude "*.map"

# HTMLファイルのキャッシュ設定（短期間）
aws s3 cp dist/ s3://$S3_BUCKET/ \
    --recursive \
    --profile $AWS_PROFILE \
    --region ap-northeast-1 \
    --exclude "*" \
    --include "*.html" \
    --metadata-directive REPLACE \
    --cache-control "max-age=300,public" \
    --content-type "text/html; charset=utf-8"

# 静的アセットのキャッシュ設定（長期間）
aws s3 cp dist/assets/ s3://$S3_BUCKET/assets/ \
    --recursive \
    --profile $AWS_PROFILE \
    --region ap-northeast-1 \
    --metadata-directive REPLACE \
    --cache-control "max-age=31536000,public,immutable"

# CloudFrontキャッシュの無効化
echo "CloudFrontキャッシュを無効化します..."
aws cloudfront create-invalidation \
    --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
    --paths "/*" \
    --profile $AWS_PROFILE

echo "================================"
echo "デプロイが完了しました！"
echo "================================"