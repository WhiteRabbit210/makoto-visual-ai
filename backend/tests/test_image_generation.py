"""
画像生成API テスト
実行日時: 2025-08-12

テスト内容:
- DALL-E 3による画像生成
- ストリーミングAPI経由での画像生成
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


class ImageGenerationTest:
    """画像生成APIのテストクラス"""
    
    def __init__(self):
        self.session = None
        self.test_results = []
        
    async def setup(self):
        """セットアップ"""
        self.session = aiohttp.ClientSession()
        
    async def teardown(self):
        """クリーンアップ"""
        if self.session:
            await self.session.close()
    
    async def test_direct_image_generation(self) -> dict:
        """画像生成サービスの直接テスト"""
        test_name = "Direct Image Generation"
        try:
            # 画像生成サービスを直接テスト
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from services.image_generation_service import image_generation_service
            
            result = await image_generation_service.generate_image(
                prompt="日本の富士山の美しい夕焼け、浮世絵風のイラスト",
                n=1,
                size="1024x1024",
                quality="medium"
            )
            
            if result and result.get('success'):
                return {
                    "test": test_name,
                    "status": "success",
                    "images": result.get('images', []),
                    "prompt": result.get('prompt')
                }
            else:
                return {
                    "test": test_name,
                    "status": "failed",
                    "error": result.get('error') if result else "No result"
                }
                
        except Exception as e:
            return {
                "test": test_name,
                "status": "error",
                "error": str(e)
            }
    
    async def test_chat_with_image_mode(self) -> dict:
        """チャットAPIの画像生成モードテスト"""
        test_name = "Chat API with Image Mode"
        try:
            # チャットストリーミングAPIをテスト
            data = {
                "messages": [
                    {
                        "role": "user",
                        "content": "美しい桜の風景を描いてください"
                    }
                ],
                "modes": ["image"],  # 画像生成モードを有効化
                "model": "gpt-4",
                "stream": True
            }
            
            async with self.session.post(
                f"{BASE_URL}/api/chat/stream",
                json=data
            ) as response:
                
                if response.status == 200:
                    # ストリーミングレスポンスを読み取る
                    events = []
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            try:
                                event_data = json.loads(line[6:])
                                events.append(event_data)
                                
                                # 画像生成イベントをチェック
                                if event_data.get('type') == 'image_generated':
                                    return {
                                        "test": test_name,
                                        "status": "success",
                                        "images": event_data.get('images', []),
                                        "event_count": len(events)
                                    }
                            except json.JSONDecodeError:
                                continue
                    
                    return {
                        "test": test_name,
                        "status": "partial",
                        "message": "Stream received but no image generated",
                        "event_count": len(events)
                    }
                else:
                    error_text = await response.text()
                    return {
                        "test": test_name,
                        "status": "failed",
                        "error": f"Status {response.status}: {error_text}"
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
        print("画像生成API テスト開始")
        print("="*60)
        
        await self.setup()
        
        try:
            # 1. 直接画像生成テスト
            print("\n[1] 画像生成サービス直接テスト...")
            result = await self.test_direct_image_generation()
            self.test_results.append(result)
            print(f"   結果: {result['status']}")
            if result['status'] == 'success' and result.get('images'):
                print(f"   生成画像数: {len(result['images'])}")
                for img in result['images']:
                    print(f"   - URL: {img.get('url', 'N/A')}")
            
            # 2. チャットAPI経由での画像生成テスト
            print("\n[2] チャットAPI画像生成モードテスト...")
            result = await self.test_chat_with_image_mode()
            self.test_results.append(result)
            print(f"   結果: {result['status']}")
            if result.get('images'):
                print(f"   生成画像数: {len(result['images'])}")
                
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
        partial_count = sum(1 for r in self.test_results if r['status'] == 'partial')
        total_count = len(self.test_results)
        
        print(f"総テスト数: {total_count}")
        print(f"成功: {success_count}")
        print(f"部分成功: {partial_count}")
        print(f"失敗: {failed_count}")
        print(f"エラー: {error_count}")
        
        if failed_count > 0 or error_count > 0:
            print("\n【失敗/エラーのテスト】")
            for result in self.test_results:
                if result['status'] in ['failed', 'error']:
                    print(f"  - {result['test']}: {result.get('error', 'Unknown error')}")
        
        # APIキーの設定状況を確認
        print("\n【設定状況】")
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('AZURE_OPENAI_IMAGE_API_KEY'):
            print("  ✅ 画像生成APIキー: 設定済み")
        else:
            print("  ❌ 画像生成APIキー: 未設定")
        
        endpoint = os.getenv('AZURE_OPENAI_IMAGE_ENDPOINT')
        if endpoint:
            print(f"  ✅ エンドポイント: {endpoint[:50]}...")
        else:
            print("  ❌ エンドポイント: 未設定")
    
    def save_results(self):
        """テスト結果をJSONファイルに保存"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_image_generation_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'test_date': datetime.now().isoformat(),
                'results': self.test_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\nテスト結果を {filename} に保存しました")


async def main():
    """メイン実行関数"""
    tester = ImageGenerationTest()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())