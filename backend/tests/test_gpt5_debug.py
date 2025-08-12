#!/usr/bin/env python3
"""
GPT-5のデバッグテスト
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

# Azure OpenAIクライアントを初期化
client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
print(f"API Version: {os.getenv('AZURE_OPENAI_API_VERSION')}")

# シンプルなテスト
try:
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "MAKOTO-gpt-5"),
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello"}
        ],
        max_completion_tokens=100
    )
    
    print(f"\n完全なレスポンス:")
    print(response)
    print(f"\n選択されたメッセージ:")
    print(response.choices[0].message)
    print(f"\nコンテンツ: '{response.choices[0].message.content}'")
    
except Exception as e:
    print(f"エラー: {e}")
    import traceback
    traceback.print_exc()