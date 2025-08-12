import os
import base64
from typing import Optional, List, Dict
import aiohttp
import json
from dotenv import load_dotenv
from utils.logger import api_logger
from io import BytesIO
from PIL import Image
import uuid
from datetime import datetime

load_dotenv()

class ImageGenerationService:
    def __init__(self):
        # 完全なURLが環境変数に設定されている
        self.endpoint = os.getenv('AZURE_OPENAI_IMAGE_ENDPOINT', 
            'https://makoto-img.openai.azure.com/openai/openai/deployments/gpt-image-1/images/generations?api-version=2025-04-01-preview')
        self.api_key = os.getenv('AZURE_OPENAI_IMAGE_API_KEY')
        self.upload_dir = os.path.join('uploads', 'generated_images')
        
        # アップロードディレクトリの作成
        os.makedirs(self.upload_dir, exist_ok=True)
        
        if not self.api_key:
            api_logger.warning("Azure OpenAI Image API key not configured")
    
    async def generate_image(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1024",
        quality: str = "medium",
        output_format: str = "url"
    ) -> Optional[Dict[str, any]]:
        """
        Azure OpenAI DALL-E 3を使用して画像を生成
        
        Args:
            prompt: 画像生成のプロンプト
            n: 生成する画像の数（DALL-E 3では1のみサポート）
            size: 画像サイズ（1024x1024, 1792x1024, 1024x1792）
            quality: 画質（standard, hd）
            output_format: 出力形式（url, b64_json）
            
        Returns:
            生成された画像情報の辞書、エラー時はNone
        """
        if not self.api_key:
            api_logger.error("Image generation API key not configured")
            return None
        
        # 環境変数から完全なURLを使用
        generation_url = self.endpoint
        
        headers = {
            "Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "output_format": "png" if output_format == "url" else output_format
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                api_logger.info(f"Generating image with prompt: {prompt[:50]}...")
                
                async with session.post(
                    generation_url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        api_logger.info(f"Successfully generated {len(result.get('data', []))} images")
                        
                        # 画像を保存してローカルURLを返す
                        processed_images = []
                        for idx, item in enumerate(result.get('data', [])):
                            if 'b64_json' in item:
                                # Base64画像を保存
                                image_data = self._save_base64_image(item['b64_json'], f"{prompt[:30]}_{idx}")
                                processed_images.append(image_data)
                            elif 'url' in item:
                                # URLをそのまま返す
                                processed_images.append({
                                    'url': item['url'],
                                    'prompt': prompt,
                                    'created_at': datetime.now().isoformat()
                                })
                        
                        return {
                            'success': True,
                            'images': processed_images,
                            'prompt': prompt
                        }
                    else:
                        error_text = await response.text()
                        api_logger.error(f"Image generation failed: {response.status} - {error_text}")
                        return {'success': False, 'error': error_text}
                        
        except aiohttp.ClientTimeout:
            api_logger.error("Image generation request timed out")
            return {'success': False, 'error': 'Request timed out'}
        except Exception as e:
            api_logger.error(f"Image generation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _save_base64_image(self, b64_data: str, filename_prefix: str) -> Dict[str, str]:
        """
        Base64エンコードされた画像を保存
        """
        try:
            # Base64をデコード
            image_data = base64.b64decode(b64_data)
            image = Image.open(BytesIO(image_data))
            
            # ファイル名を生成
            file_id = str(uuid.uuid4())
            filename = f"{filename_prefix}_{file_id}.png"
            file_path = os.path.join(self.upload_dir, filename)
            
            # 画像を保存
            image.save(file_path, 'PNG')
            
            # 相対URLを返す
            relative_url = f"/uploads/generated_images/{filename}"
            
            return {
                'url': relative_url,
                'file_path': file_path,
                'filename': filename,
                'created_at': datetime.now().isoformat()
            }
        except Exception as e:
            api_logger.error(f"Failed to save image: {str(e)}")
            raise

# シングルトンインスタンス
image_generation_service = ImageGenerationService()