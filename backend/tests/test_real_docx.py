"""
実際のDOCXファイルでのテスト
チームC キャラクター詳細設定.docxを使用

実行日時: 2025-08-13
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000"
DOCX_FILE = "/home/whiterabbit/Projects/makoto_ui-1/チームC キャラクター詳細設定.docx"


async def test_real_docx():
    """実際のDOCXファイルでテスト"""
    
    # ファイルの存在確認
    file_path = Path(DOCX_FILE)
    if not file_path.exists():
        print(f"エラー: ファイルが見つかりません: {DOCX_FILE}")
        return
    
    file_size = file_path.stat().st_size
    print(f"ファイル情報:")
    print(f"  パス: {DOCX_FILE}")
    print(f"  サイズ: {file_size:,} バイト")
    
    async with aiohttp.ClientSession() as session:
        # 1. テスト用ライブラリを作成
        print("\n[1] ライブラリ作成...")
        data = {
            "name": f"DOCXテスト_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "実際のDOCXファイルテスト"
        }
        
        async with session.post(f"{BASE_URL}/api/libraries", json=data) as response:
            if response.status != 200:
                print(f"  エラー: ライブラリ作成失敗 (status: {response.status})")
                return
            
            result = await response.json()
            library_id = result['id']
            print(f"  成功: ライブラリID = {library_id}")
        
        # 2. DOCXファイルをアップロード
        print("\n[2] DOCXファイルアップロード...")
        
        # ファイルを読み込み
        with open(DOCX_FILE, 'rb') as f:
            file_content = f.read()
        
        # FormDataを作成
        data = aiohttp.FormData()
        data.add_field('file', 
                      file_content, 
                      filename='チームC キャラクター詳細設定.docx',
                      content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        
        async with session.post(
            f"{BASE_URL}/api/libraries/{library_id}/files",
            data=data
        ) as response:
            response_text = await response.text()
            
            if response.status == 200:
                result = json.loads(response_text)
                print(f"  成功: ファイルアップロード完了")
                print(f"  ファイル名: {result.get('filename')}")
                print(f"  サイズ: {result.get('size'):,} バイト")
            else:
                print(f"  エラー: アップロード失敗 (status: {response.status})")
                print(f"  詳細: {response_text}")
                
                # クリーンアップ
                await session.delete(f"{BASE_URL}/api/libraries/{library_id}")
                return
        
        # 3. テキスト抽出
        print("\n[3] テキスト抽出...")
        filename = 'チームC キャラクター詳細設定.docx'
        
        async with session.get(
            f"{BASE_URL}/api/libraries/{library_id}/files/{filename}/text"
        ) as response:
            if response.status == 200:
                result = await response.json()
                text = result.get('text', '')
                metadata = result.get('metadata', {})
                
                print(f"  成功: テキスト抽出完了")
                print(f"  フォーマット: {metadata.get('format')}")
                print(f"  段落数: {metadata.get('paragraph_count')}")
                print(f"  テーブル数: {metadata.get('table_count')}")
                print(f"  抽出文字数: {len(text):,}")
                
                # テキストの最初の500文字を表示
                print(f"\n[抽出されたテキスト (最初の500文字)]")
                print("-" * 60)
                print(text[:500])
                print("-" * 60)
                
                # キャラクター名が含まれているか確認
                print(f"\n[キャラクター名の確認]")
                character_names = ["愛", "勇気", "知恵", "春香", "夏美", "秋子", "冬華"]
                for name in character_names:
                    if name in text:
                        print(f"  ✅ {name}: 含まれている")
                    else:
                        print(f"  ❌ {name}: 見つからない")
                
            else:
                error_text = await response.text()
                print(f"  エラー: テキスト抽出失敗 (status: {response.status})")
                print(f"  詳細: {error_text}")
        
        # 4. クリーンアップ
        print("\n[4] クリーンアップ...")
        
        # ファイル削除
        await session.delete(f"{BASE_URL}/api/libraries/{library_id}/files/{filename}")
        
        # ライブラリ削除
        await session.delete(f"{BASE_URL}/api/libraries/{library_id}")
        print("  完了: テストデータを削除しました")


async def main():
    """メイン実行関数"""
    print("\n" + "="*60)
    print("実際のDOCXファイルテスト")
    print("="*60)
    
    await test_real_docx()
    
    print("\n" + "="*60)
    print("テスト完了")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())