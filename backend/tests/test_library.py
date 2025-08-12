"""
ライブラリAPI テスト
実行日時: 2025-08-12

テスト内容:
- ライブラリCRUD操作
- ファイルアップロード/ダウンロード
- エンベディング管理
- ベクトル検索
"""

import asyncio
import aiohttp
import json
import io
from datetime import datetime
from typing import Dict, Any, List

BASE_URL = "http://localhost:8000"


class LibraryV2APITest:
    """ライブラリAPIのテストクラス"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        self.created_library_ids = []  # クリーンアップ用
        
    async def setup(self):
        """セットアップ"""
        self.session = aiohttp.ClientSession()
        
    async def teardown(self):
        """クリーンアップ"""
        # 作成したライブラリを削除
        for library_id in self.created_library_ids:
            try:
                await self.session.delete(f"{BASE_URL}/api/libraries/{library_id}")
            except:
                pass
                
        if self.session:
            await self.session.close()
    
    async def test_create_library(self) -> Dict[str, Any]:
        """ライブラリ作成テスト"""
        test_name = "Create Library"
        try:
            data = {
                "name": f"テストライブラリ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "description": "テスト用のライブラリです",
                "metadata": {
                    "category": "test",
                    "created_by": "test_script"
                }
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/libraries",
                json=data
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    self.created_library_ids.append(result['id'])
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": result['id'],
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_get_libraries(self) -> Dict[str, Any]:
        """ライブラリ一覧取得テスト"""
        test_name = "Get Libraries"
        try:
            async with self.session.get(f"{BASE_URL}/api/libraries") as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "count": len(result),
                        "data": result[:3] if result else []  # 最初の3件のみ
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_get_library_detail(self, library_id: str) -> Dict[str, Any]:
        """ライブラリ詳細取得テスト"""
        test_name = "Get Library Detail"
        try:
            async with self.session.get(f"{BASE_URL}/api/libraries/{library_id}") as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_update_library(self, library_id: str) -> Dict[str, Any]:
        """ライブラリ更新テスト"""
        test_name = "Update Library"
        try:
            data = {
                "name": f"更新されたライブラリ_{datetime.now().strftime('%H%M%S')}",
                "description": "更新されたテスト用ライブラリ",
                "metadata": {
                    "category": "test",
                    "updated_by": "test_script",
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            async with self.session.put(
                f"{BASE_URL}/api/libraries/{library_id}",
                json=data
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_upload_file(self, library_id: str) -> Dict[str, Any]:
        """ファイルアップロードテスト"""
        test_name = "Upload File"
        try:
            # テスト用のテキストファイルを作成
            text_content = """これはテスト用のテキストファイルです。
ライブラリAPIのファイルアップロード機能をテストしています。
日本語の内容も正しく処理されることを確認します。

テストデータ:
- 項目1: テストデータA
- 項目2: テストデータB
- 項目3: テストデータC
"""
            
            # FormDataを作成
            data = aiohttp.FormData()
            data.add_field('file',
                          io.BytesIO(text_content.encode('utf-8')),
                          filename='test_document.txt',
                          content_type='text/plain')
            
            async with self.session.post(
                f"{BASE_URL}/api/libraries/{library_id}/files",
                data=data
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "filename": result.get('filename'),
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_download_file(self, library_id: str, filename: str) -> Dict[str, Any]:
        """ファイルダウンロードテスト"""
        test_name = "Download File"
        try:
            async with self.session.get(
                f"{BASE_URL}/api/libraries/{library_id}/files/{filename}"
            ) as response:
                
                if response.status == 200:
                    content = await response.read()
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "filename": filename,
                        "content_size": len(content),
                        "content_type": response.headers.get('content-type')
                    }
                else:
                    result = await response.json()
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_extract_text(self, library_id: str, filename: str) -> Dict[str, Any]:
        """テキスト抽出テスト"""
        test_name = "Extract Text"
        try:
            async with self.session.get(
                f"{BASE_URL}/api/libraries/{library_id}/files/{filename}/text"
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "filename": filename,
                        "text_length": len(result.get('text', '')),
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_start_embeddings(self, library_id: str) -> Dict[str, Any]:
        """エンベディング開始テスト"""
        test_name = "Start Embeddings"
        try:
            data = {
                "force_update": False
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/libraries/{library_id}/embeddings",
                json=data
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "job_id": result.get('job_id'),
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_get_embedding_status(self, library_id: str) -> Dict[str, Any]:
        """エンベディング状態確認テスト"""
        test_name = "Get Embedding Status"
        try:
            async with self.session.get(
                f"{BASE_URL}/api/libraries/{library_id}/embeddings/status"
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "embedding_status": result.get('status'),
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_search_library(self, library_id: str) -> Dict[str, Any]:
        """ベクトル検索テスト"""
        test_name = "Search Library (Vector)"
        try:
            data = {
                "query": "テストデータ",
                "top_k": 5,
                "threshold": 0.7
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/libraries/{library_id}/search",
                json=data
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "results_count": len(result.get('results', [])),
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_delete_file(self, library_id: str, filename: str) -> Dict[str, Any]:
        """ファイル削除テスト"""
        test_name = "Delete File"
        try:
            async with self.session.delete(
                f"{BASE_URL}/api/libraries/{library_id}/files/{filename}"
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "filename": filename,
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_delete_library(self, library_id: str) -> Dict[str, Any]:
        """ライブラリ削除テスト"""
        test_name = "Delete Library"
        try:
            async with self.session.delete(
                f"{BASE_URL}/api/libraries/{library_id}"
            ) as response:
                result = await response.json()
                
                if response.status == 200:
                    # 削除成功したらリストから除外
                    if library_id in self.created_library_ids:
                        self.created_library_ids.remove(library_id)
                    
                    return {
                        "test": test_name,
                        "status": "success",
                        "library_id": library_id,
                        "data": result
                    }
                else:
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}",
                        "detail": result
                    }
                    
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def run_all_tests(self):
        """全テストを実行"""
        print("\n" + "="*60)
        print("ライブラリAPI テスト開始")
        print("="*60)
        
        await self.setup()
        
        try:
            # 1. ライブラリ作成
            print("\n[1] ライブラリ作成テスト...")
            result = await self.test_create_library()
            self.test_results.append(result)
            library_id = result.get('library_id') if result['status'] == 'success' else None
            print(f"   結果: {result['status']}")
            if library_id:
                print(f"   Library ID: {library_id}")
            
            # 2. ライブラリ一覧取得
            print("\n[2] ライブラリ一覧取得テスト...")
            result = await self.test_get_libraries()
            self.test_results.append(result)
            print(f"   結果: {result['status']}")
            if result['status'] == 'success':
                print(f"   ライブラリ数: {result['count']}")
            
            if library_id:
                # 3. ライブラリ詳細取得
                print("\n[3] ライブラリ詳細取得テスト...")
                result = await self.test_get_library_detail(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
                # 4. ライブラリ更新
                print("\n[4] ライブラリ更新テスト...")
                result = await self.test_update_library(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
                # 5. ファイルアップロード
                print("\n[5] ファイルアップロードテスト...")
                upload_result = await self.test_upload_file(library_id)
                self.test_results.append(upload_result)
                print(f"   結果: {upload_result['status']}")
                filename = upload_result.get('filename') if upload_result['status'] == 'success' else None
                
                if filename:
                    # 6. ファイルダウンロード
                    print("\n[6] ファイルダウンロードテスト...")
                    result = await self.test_download_file(library_id, filename)
                    self.test_results.append(result)
                    print(f"   結果: {result['status']}")
                    
                    # 7. テキスト抽出
                    print("\n[7] テキスト抽出テスト...")
                    result = await self.test_extract_text(library_id, filename)
                    self.test_results.append(result)
                    print(f"   結果: {result['status']}")
                    
                    # 8. ファイル削除
                    print("\n[8] ファイル削除テスト...")
                    result = await self.test_delete_file(library_id, filename)
                    self.test_results.append(result)
                    print(f"   結果: {result['status']}")
                
                # 9. エンベディング開始
                print("\n[9] エンベディング開始テスト...")
                result = await self.test_start_embeddings(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
                # 10. エンベディング状態確認
                print("\n[10] エンベディング状態確認テスト...")
                result = await self.test_get_embedding_status(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
                # 11. ベクトル検索
                print("\n[11] ベクトル検索テスト...")
                result = await self.test_search_library(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
                # 12. ライブラリ削除
                print("\n[12] ライブラリ削除テスト...")
                result = await self.test_delete_library(library_id)
                self.test_results.append(result)
                print(f"   結果: {result['status']}")
                
        finally:
            await self.teardown()
        
        # 結果サマリー
        self.print_summary()
        
        # 結果をJSONファイルに保存
        self.save_results()
    
    def print_summary(self):
        """テスト結果サマリーを表示"""
        print("\n" + "="*60)
        print("テスト結果サマリー")
        print("="*60)
        
        success_count = sum(1 for r in self.test_results if r['status'] == 'success')
        failed_count = sum(1 for r in self.test_results if r['status'] == 'failed')
        error_count = sum(1 for r in self.test_results if r['status'] == 'error')
        total_count = len(self.test_results)
        
        print(f"総テスト数: {total_count}")
        print(f"成功: {success_count}")
        print(f"失敗: {failed_count}")
        print(f"エラー: {error_count}")
        
        if failed_count > 0 or error_count > 0:
            print("\n【失敗/エラーのテスト】")
            for result in self.test_results:
                if result['status'] in ['failed', 'error']:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
    
    def save_results(self):
        """テスト結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_library_v2_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'results': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\nテスト結果を {filename} に保存しました")


async def main():
    """メイン実行関数"""
    tester = LibraryV2APITest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())