#!/bin/bash

# Lambda Layer ビルドスクリプト
# Python 3.11用のLambda Layerを作成

set -e

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Lambda Layer ビルドを開始します...${NC}"

# 変数定義
LAYER_NAME="makoto-common-layer"
PYTHON_VERSION="python3.11"
BUILD_DIR="build"
LAYER_DIR="${BUILD_DIR}/python"
ZIP_FILE="${LAYER_NAME}.zip"

# クリーンアップ
echo -e "${YELLOW}既存のビルドディレクトリをクリーンアップ...${NC}"
rm -rf ${BUILD_DIR}
rm -f ${ZIP_FILE}

# ディレクトリ作成
echo -e "${YELLOW}ビルドディレクトリを作成...${NC}"
mkdir -p ${LAYER_DIR}

# Pythonパッケージをコピー
echo -e "${YELLOW}Pythonパッケージをコピー...${NC}"
cp -r python/makoto_common ${LAYER_DIR}/

# 依存パッケージをインストール
echo -e "${YELLOW}依存パッケージをインストール...${NC}"
pip install -r requirements.txt -t ${LAYER_DIR} --no-cache-dir --upgrade

# 不要なファイルを削除
echo -e "${YELLOW}不要なファイルを削除...${NC}"
find ${LAYER_DIR} -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find ${LAYER_DIR} -type f -name "*.pyc" -delete
find ${LAYER_DIR} -type f -name "*.pyo" -delete
find ${LAYER_DIR} -type d -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find ${LAYER_DIR} -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find ${LAYER_DIR} -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

# ZIPファイル作成
echo -e "${YELLOW}ZIPファイルを作成...${NC}"
cd ${BUILD_DIR}
zip -r ../${ZIP_FILE} python -q
cd ..

# ファイルサイズ確認
FILE_SIZE=$(du -h ${ZIP_FILE} | cut -f1)
echo -e "${GREEN}ビルド完了: ${ZIP_FILE} (${FILE_SIZE})${NC}"

# Lambda Layer制限チェック（262,144,000 bytes = 250MB）
MAX_SIZE=262144000
ACTUAL_SIZE=$(stat -f%z ${ZIP_FILE} 2>/dev/null || stat -c%s ${ZIP_FILE})

if [ ${ACTUAL_SIZE} -gt ${MAX_SIZE} ]; then
    echo -e "${RED}警告: ZIPファイルサイズがLambda Layerの制限（250MB）を超えています！${NC}"
    echo -e "${RED}実際のサイズ: $(echo "scale=2; ${ACTUAL_SIZE}/1024/1024" | bc)MB${NC}"
    exit 1
fi

echo -e "${GREEN}Lambda Layerのビルドが完了しました！${NC}"
echo ""
echo "次のステップ:"
echo "  1. Layerをデプロイ: ./deploy.sh"
echo "  2. 手動でアップロード: aws lambda publish-layer-version --layer-name ${LAYER_NAME} --zip-file fileb://${ZIP_FILE} --compatible-runtimes ${PYTHON_VERSION}"