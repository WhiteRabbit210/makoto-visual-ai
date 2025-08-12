#!/usr/bin/env python3
"""
Webクロールのパフォーマンステスト
"""

import time
import asyncio
from dotenv import load_dotenv
load_dotenv()

import sys
sys.path.insert(0, '/home/whiterabbit/Projects/makoto_ui-1/makoto/backend')

from services.web_crawler_service import web_crawler_service

async def test_crawl_performance():
    """クロールパフォーマンスのテスト"""
    
    # テスト1: 要約ありの場合
    print("テスト1: 要約あり")
    start = time.time()
    result1 = await web_crawler_service.search_and_crawl(
        keywords=["python", "programming"],
        original_query="Pythonプログラミングについて",
        skip_summary=False
    )
    end = time.time()
    print(f"  - 結果: {len(result1.get('sources', []))}件のソース")
    print(f"  - 時間: {end - start:.2f}秒\n")
    
    # テスト2: 要約なしの場合
    print("テスト2: 要約なし（高速化）")
    start = time.time()
    result2 = await web_crawler_service.search_and_crawl(
        keywords=["python", "programming"],
        original_query="Pythonプログラミングについて",
        skip_summary=True
    )
    end = time.time()
    print(f"  - 結果: {len(result2.get('sources', []))}件のソース")
    print(f"  - 時間: {end - start:.2f}秒\n")
    
    # テスト3: 並列クロール
    print("テスト3: 複数キーワードの並列処理")
    start = time.time()
    tasks = []
    keywords_list = [
        ["python", "tutorial"],
        ["javascript", "framework"],
        ["rust", "programming"]
    ]
    
    for keywords in keywords_list:
        task = web_crawler_service.search_and_crawl(
            keywords=keywords,
            original_query=f"{keywords[0]}について",
            skip_summary=True
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    end = time.time()
    
    total_sources = sum(len(r.get('sources', [])) for r in results)
    print(f"  - 結果: 合計{total_sources}件のソース")
    print(f"  - 時間: {end - start:.2f}秒（3つの検索を並列実行）")

if __name__ == "__main__":
    asyncio.run(test_crawl_performance())