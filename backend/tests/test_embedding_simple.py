#!/usr/bin/env python3
"""
エンベディングAPIの単純な接続テスト
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトのルートをPythonパスに追加
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

# OpenAIのインポート
from openai import AsyncAzureOpenAI


async def test_connection():
    """接続テスト"""
    
    # 環境変数チェック
    endpoint = os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY')
    deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')
    api_version = os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION', '2024-12-01-preview')
    
    print("環境変数:")
    print(f"  Endpoint: {endpoint}")
    print(f"  API Key: {api_key[:20]}...")
    print(f"  Deployment: {deployment}")
    print(f"  API Version: {api_version}")
    print()
    
    # クライアント作成
    client = AsyncAzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=endpoint
    )
    
    # テスト実行
    try:
        print("エンベディング作成中...")
        response = await client.embeddings.create(
            model=deployment,
            input="test"
        )
        
        embedding = response.data[0].embedding
        print(f"✅ 成功: ベクトル次元数 = {len(embedding)}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_connection())