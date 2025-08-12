"""
バイナリファイル（DOCX等）のストレージテスト
ローカルストレージでの動作確認

実行日時: 2025-08-13
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from pathlib import Path
import base64

BASE_URL = "http://localhost:8000"
DOCX_FILE = "/home/whiterabbit/Projects/makoto_ui-1/チームC キャラクター詳細設定.docx"


async def test_binary_storage():
    """バイナリファイルのストレージテスト"""
    
    # ファイルの存在確認
    file_path = Path(DOCX_FILE)
    if not file_path.exists():
        print(f"エラー: ファイルが見つかりません: {DOCX_FILE}")
        return
    
    file_size = file_path.stat().st_size
    print(f"テストファイル情報:")
    print(f"  パス: {DOCX_FILE}")
    print(f"  サイズ: {file_size:,} バイト")
    
    async with aiohttp.ClientSession() as session:
        # 1. テスト用ライブラリを作成
        print("\n[1] ライブラリ作成...")
        data = {
            "name": f"バイナリストレージテスト_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "description": "バイナリファイルストレージのテスト"
        }
        
        async with session.post(f"{BASE_URL}/api/libraries", json=data) as response:
            if response.status != 200:
                print(f"  エラー: ライブラリ作成失敗 (status: {response.status})")
                error = await response.text()
                print(f"  詳細: {error}")
                return
            
            result = await response.json()
            library_id = result['id']
            print(f"  成功: ライブラリID = {library_id}")
        
        # 2. DOCXファイルをアップロード
        print("\n[2] DOCXファイルアップロード...")
        
        # ファイルを読み込み
        with open(DOCX_FILE, 'rb') as f:
            file_content = f.read()
        
        print(f"  読み込んだファイルサイズ: {len(file_content):,} バイト")
        
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
                print(f"  保存サイズ: {result.get('size'):,} バイト")
                print(f"  コンテンツタイプ: {result.get('content_type')}")
            else:
                print(f"  エラー: アップロード失敗 (status: {response.status})")
                print(f"  詳細: {response_text}")
                # クリーンアップ
                await session.delete(f"{BASE_URL}/api/libraries/{library_id}")
                return
        
        # 3. ファイルダウンロード（バイナリ取得）
        print("\n[3] ファイルダウンロード...")
        filename = 'チームC キャラクター詳細設定.docx'
        
        async with session.get(
            f"{BASE_URL}/api/libraries/{library_id}/files/{filename}"
        ) as response:
            if response.status == 200:
                # バイナリコンテンツを取得
                downloaded_content = await response.read()
                print(f"  成功: ファイルダウンロード完了")
                print(f"  ダウンロードサイズ: {len(downloaded_content):,} バイト")
                
                # 元のファイルと比較
                if downloaded_content == file_content:
                    print(f"  ✅ ファイル内容が一致（バイナリ完全一致）")
                else:
                    print(f"  ❌ ファイル内容が不一致")
                    print(f"    元のサイズ: {len(file_content)} バイト")
                    print(f"    ダウンロードサイズ: {len(downloaded_content)} バイト")
                    
                    # 最初の100バイトを比較
                    print(f"    元の最初の100バイト: {file_content[:100].hex()}")
                    print(f"    DLの最初の100バイト: {downloaded_content[:100].hex()}")
            else:
                error_text = await response.text()
                print(f"  エラー: ダウンロード失敗 (status: {response.status})")
                print(f"  詳細: {error_text}")
        
        # 4. テキスト抽出（document_extractorのテスト）
        print("\n[4] テキスト抽出...")
        
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
                
                # テキストの最初の200文字を表示
                print(f"\n  [抽出されたテキスト (最初の200文字)]")
                print(f"  {'-' * 50}")
                print(f"  {text[:200]}")
                print(f"  {'-' * 50}")
                
                # キャラクター名が含まれているか確認
                print(f"\n  [キャラクター名の確認]")
                character_names = ["愛", "勇気", "知恵", "春香", "夏美", "秋子", "冬華"]
                found_count = 0
                for name in character_names:
                    if name in text:
                        print(f"    ✅ {name}: 含まれている")
                        found_count += 1
                    else:
                        print(f"    ❌ {name}: 見つからない")
                
                if found_count > 0:
                    print(f"  → {found_count}/{len(character_names)} のキャラクター名を検出")
            else:
                error_text = await response.text()
                print(f"  エラー: テキスト抽出失敗 (status: {response.status})")
                print(f"  詳細: {error_text}")
        
        # 5. ライブラリ一覧確認
        print("\n[5] ライブラリ一覧取得...")
        
        async with session.get(f"{BASE_URL}/api/libraries") as response:
            if response.status == 200:
                libraries = await response.json()
                
                # テストライブラリが含まれているか確認
                test_library = next((lib for lib in libraries if lib['id'] == library_id), None)
                if test_library:
                    print(f"  成功: テストライブラリが一覧に存在")
                    print(f"    名前: {test_library['name']}")
                    print(f"    ファイル数: {test_library['file_count']}")
                    print(f"    合計サイズ: {test_library['total_size']:,} バイト")
                else:
                    print(f"  エラー: テストライブラリが一覧に見つからない")
        
        # 6. ライブラリ詳細確認
        print("\n[6] ライブラリ詳細取得...")
        
        async with session.get(f"{BASE_URL}/api/libraries/{library_id}") as response:
            if response.status == 200:
                library_detail = await response.json()
                print(f"  成功: ライブラリ詳細取得")
                print(f"    ファイル数: {len(library_detail.get('files', []))}")
                
                if library_detail.get('files'):
                    for file_info in library_detail['files']:
                        print(f"    ファイル: {file_info['name']}")
                        print(f"      サイズ: {file_info['size']:,} バイト")
                        print(f"      タイプ: {file_info['content_type']}")
                        print(f"      アップロード: {file_info['uploaded_at']}")
        
        # 7. クリーンアップ
        print("\n[7] クリーンアップ...")
        
        # ファイル削除
        async with session.delete(f"{BASE_URL}/api/libraries/{library_id}/files/{filename}") as response:
            if response.status == 200:
                print(f"  ファイル削除: 成功")
            else:
                print(f"  ファイル削除: 失敗 (status: {response.status})")
        
        # ライブラリ削除
        async with session.delete(f"{BASE_URL}/api/libraries/{library_id}") as response:
            if response.status == 200:
                print(f"  ライブラリ削除: 成功")
            else:
                print(f"  ライブラリ削除: 失敗 (status: {response.status})")
        
        print("\n[テスト完了] バイナリファイルのストレージテストが完了しました")


async def test_storage_internals():
    """ストレージ内部動作の確認（ローカルストレージ）"""
    print("\n" + "="*60)
    print("ストレージ内部動作テスト（ローカル）")
    print("="*60)
    
    # sys.pathを追加してインポート
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from services.storage_service import storage_service
    
    # ストレージタイプの確認
    print(f"\n[ストレージ設定]")
    print(f"  ストレージタイプ: {storage_service.storage_type.value}")
    
    if storage_service.storage_type.value == 'local':
        print(f"  ローカルストレージパス: uploads/")
        
        # テスト用バイナリデータ
        test_binary = b'\x50\x4b\x03\x04\x14\x00\x06\x00'  # DOCXのマジックナンバー
        test_key = "test/binary/test.docx"
        
        # バイナリデータの保存テスト
        print(f"\n[バイナリ保存テスト]")
        result = await storage_service.put_object(
            key=test_key,
            content=test_binary,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        print(f"  保存結果: {result}")
        
        # バイナリデータの取得テスト
        print(f"\n[バイナリ取得テスト]")
        retrieved = await storage_service.get_object(test_key, return_bytes=True)
        if retrieved == test_binary:
            print(f"  ✅ バイナリデータが正しく取得できました")
        else:
            print(f"  ❌ バイナリデータが一致しません")
            print(f"    元: {test_binary.hex()}")
            print(f"    取得: {retrieved.hex() if retrieved else 'None'}")
        
        # クリーンアップ
        await storage_service.delete_object(test_key)
        print(f"  テストデータを削除しました")


async def main():
    """メイン実行関数"""
    print("\n" + "="*60)
    print("バイナリファイルストレージテスト")
    print("="*60)
    
    # APIテスト
    await test_binary_storage()
    
    # 内部動作テスト
    await test_storage_internals()
    
    print("\n" + "="*60)
    print("全テスト完了")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())