#!/usr/bin/env python3
"""
エンベディングサービスのテスト
Azure OpenAI text-embedding-3-large の動作確認

実行日時: 2025-08-13
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトのルートをPythonパスに追加
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv(backend_dir / '.env')

# 環境変数の確認
print("=" * 60)
print("環境変数の確認")
print("=" * 60)
print(f"AZURE_OPENAI_EMBEDDING_ENDPOINT: {os.getenv('AZURE_OPENAI_EMBEDDING_ENDPOINT')}")
print(f"AZURE_OPENAI_EMBEDDING_API_KEY: {os.getenv('AZURE_OPENAI_EMBEDDING_API_KEY')[:10]}...")
print(f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT')}")
print(f"AZURE_OPENAI_EMBEDDING_API_VERSION: {os.getenv('AZURE_OPENAI_EMBEDDING_API_VERSION')}")
print()


async def test_embedding_creation():
    """エンベディング作成のテスト"""
    from services.embedding_service import embedding_service
    
    print("=" * 60)
    print("テスト1: 単純なテキストのエンベディング")
    print("=" * 60)
    
    test_text = "これはテスト用のテキストです。Azure OpenAI text-embedding-3-largeが正しく動作することを確認します。"
    
    try:
        # エンベディング作成
        embedding = await embedding_service.create_embedding(test_text)
        
        print(f"✅ エンベディング作成成功")
        print(f"  - ベクトル次元数: {len(embedding)}")
        print(f"  - 最初の5要素: {embedding[:5]}")
        print(f"  - 型: {type(embedding)}")
        
        # 期待される次元数の確認
        expected_dim = 3072
        if len(embedding) == expected_dim:
            print(f"  - ✅ 次元数が正しい: {expected_dim}")
        else:
            print(f"  - ❌ 次元数が異なる: 期待={expected_dim}, 実際={len(embedding)}")
        
        return True
        
    except Exception as e:
        print(f"❌ エンベディング作成失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_chunk_creation():
    """テキストチャンク化のテスト"""
    from services.embedding_service import embedding_service
    
    print("=" * 60)
    print("テスト2: テキストのチャンク化")
    print("=" * 60)
    
    # 長いテキストを作成
    long_text = """
    MAKOTOは、高度なAI技術を活用した対話型アシスタントです。
    自然言語処理、画像生成、音声認識など、様々な機能を提供します。
    
    主な機能：
    1. チャット機能 - 自然な対話が可能
    2. 画像生成 - DALL-E 3を使用した高品質な画像生成
    3. ドキュメント処理 - PDF、Word、Excel、PowerPointなどのファイルを処理
    4. ベクトル検索 - セマンティック検索によるコンテンツ検索
    
    技術スタック：
    - バックエンド: FastAPI (Python)
    - フロントエンド: Vue.js 3
    - AI: Azure OpenAI (GPT-4.1, text-embedding-3-large)
    - ストレージ: AWS S3 / Azure Blob Storage
    - データベース: DynamoDB / CosmosDB
    
    このシステムは、マルチテナント対応で、高いスケーラビリティを持っています。
    """ * 5  # 長いテキストにするために5回繰り返す
    
    # チャンク化
    chunks = embedding_service.create_chunks(long_text, "test_document.txt")
    
    print(f"✅ チャンク作成完了")
    print(f"  - チャンク数: {len(chunks)}")
    print(f"  - 各チャンクのサイズ:")
    for i, chunk in enumerate(chunks[:3]):  # 最初の3つだけ表示
        print(f"    - チャンク{i+1}: {len(chunk.text)}文字")
        print(f"      開始位置: {chunk.metadata['start_position']}")
        print(f"      終了位置: {chunk.metadata['end_position']}")
    
    return True


async def test_cosine_similarity():
    """コサイン類似度計算のテスト"""
    from services.embedding_service import embedding_service
    import numpy as np
    
    print("=" * 60)
    print("テスト3: コサイン類似度の計算")
    print("=" * 60)
    
    # テスト用ベクトル
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]  # vec1と同じ（類似度1.0）
    vec3 = [0.0, 1.0, 0.0]  # vec1と直交（類似度0.0）
    vec4 = [-1.0, 0.0, 0.0]  # vec1と逆向き（類似度-1.0）
    
    # 類似度計算
    sim1 = embedding_service.cosine_similarity(vec1, vec2)
    sim2 = embedding_service.cosine_similarity(vec1, vec3)
    sim3 = embedding_service.cosine_similarity(vec1, vec4)
    
    print(f"✅ コサイン類似度計算完了")
    print(f"  - 同一ベクトル: {sim1:.4f} (期待値: 1.0)")
    print(f"  - 直交ベクトル: {sim2:.4f} (期待値: 0.0)")
    print(f"  - 逆向きベクトル: {sim3:.4f} (期待値: -1.0)")
    
    # 許容誤差の確認
    tolerance = 0.0001
    assert abs(sim1 - 1.0) < tolerance, f"同一ベクトルの類似度が1.0ではない: {sim1}"
    assert abs(sim2 - 0.0) < tolerance, f"直交ベクトルの類似度が0.0ではない: {sim2}"
    assert abs(sim3 - (-1.0)) < tolerance, f"逆向きベクトルの類似度が-1.0ではない: {sim3}"
    
    print("  - ✅ すべての計算が正しい")
    
    return True


async def test_semantic_similarity():
    """意味的類似度のテスト（実際のエンベディングを使用）"""
    from services.embedding_service import embedding_service
    
    print("=" * 60)
    print("テスト4: 意味的類似度の計算")
    print("=" * 60)
    
    # 意味的に似た文章と異なる文章
    text1 = "機械学習は人工知能の一分野です"
    text2 = "AIの中でも機械学習は重要な技術です"  # text1と意味的に近い
    text3 = "今日の天気は晴れです"  # text1と意味的に遠い
    
    try:
        # エンベディング作成
        print("エンベディングを作成中...")
        emb1 = await embedding_service.create_embedding(text1)
        emb2 = await embedding_service.create_embedding(text2)
        emb3 = await embedding_service.create_embedding(text3)
        
        # 類似度計算
        sim_12 = embedding_service.cosine_similarity(emb1, emb2)
        sim_13 = embedding_service.cosine_similarity(emb1, emb3)
        
        print(f"✅ 意味的類似度計算完了")
        print(f"  - テキスト1: {text1}")
        print(f"  - テキスト2: {text2}")
        print(f"  - テキスト3: {text3}")
        print()
        print(f"  - 類似度(1-2): {sim_12:.4f} (意味的に近い)")
        print(f"  - 類似度(1-3): {sim_13:.4f} (意味的に遠い)")
        
        # 期待される結果の確認
        if sim_12 > sim_13:
            print(f"  - ✅ 意味的に近い文章の類似度が高い")
        else:
            print(f"  - ❌ 類似度の大小関係が期待と異なる")
        
        return True
        
    except Exception as e:
        print(f"❌ 意味的類似度計算失敗: {e}")
        return False


async def main():
    """メインテスト実行"""
    print("=" * 60)
    print("エンベディングサービステスト開始")
    print("=" * 60)
    print()
    
    results = []
    
    # テスト1: エンベディング作成
    result1 = await test_embedding_creation()
    results.append(("エンベディング作成", result1))
    print()
    
    # テスト2: チャンク化
    result2 = await test_chunk_creation()
    results.append(("チャンク化", result2))
    print()
    
    # テスト3: コサイン類似度
    result3 = await test_cosine_similarity()
    results.append(("コサイン類似度", result3))
    print()
    
    # テスト4: 意味的類似度
    result4 = await test_semantic_similarity()
    results.append(("意味的類似度", result4))
    print()
    
    # 結果サマリー
    print("=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"  - {test_name}: {status}")
    
    print()
    print(f"成功: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 すべてのテストが成功しました！")
    else:
        print("⚠️  一部のテストが失敗しました")
    
    return success_count == total_count


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)