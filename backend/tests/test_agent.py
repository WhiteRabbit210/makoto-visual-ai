#!/usr/bin/env python3
"""
エージェントAPIの詳細テスト
"""

import sys
import os
from dotenv import load_dotenv

# 環境変数を先に設定
load_dotenv()

# パスを追加
sys.path.insert(0, '/home/whiterabbit/Projects/makoto_ui-1/makoto/backend')

from backend_types.api_types import AnalyzeRequest
from api.agent import analyze_prompt
import asyncio
import traceback

async def test_agent():
    """エージェント分析のテスト"""
    try:
        request = AnalyzeRequest(
            prompt="東京の天気を教えて",
            context=[]
        )
        
        print("エージェント分析リクエスト送信...")
        result = await analyze_prompt(request)
        print(f"成功: {result}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        print(f"詳細: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agent())
    sys.exit(0 if success else 1)