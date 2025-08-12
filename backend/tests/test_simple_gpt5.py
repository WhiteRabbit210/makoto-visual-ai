#!/usr/bin/env python3
"""
GPT-5の単純なテスト
"""

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAIクライアントを初期化
client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# シンプルなテスト
response = client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "MAKOTO-gpt-5"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in Japanese"}
    ],
    max_completion_tokens=100
)

print(f"応答: {response.choices[0].message.content}")