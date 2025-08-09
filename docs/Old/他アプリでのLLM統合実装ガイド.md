# 他アプリでのLLM統合実装ガイド

このドキュメントは、別のアプリケーションでこのプロジェクトと同様のLLM統合を実装したい開発者向けのガイドです。

## 1. 基本セットアップ

### 1.1 必要なライブラリのインストール

```bash
# Python環境
pip install openai==1.3.0
pip install fastapi
pip install uvicorn
pip install aiohttp
pip install python-dotenv

# Node.js環境（フロントエンド）
npm install axios
npm install @types/node
```

### 1.2 環境変数の設定

`.env`ファイルを作成し、以下の設定を追加：

```env
# Azure OpenAI設定
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# 画像生成用（オプション）
AZURE_OPENAI_IMAGE_ENDPOINT=https://your-image-resource.openai.azure.com/
AZURE_OPENAI_IMAGE_API_KEY=your_image_api_key

# その他の設定
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 1.3 Azure OpenAIクライアントの初期化

```python
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# グローバルクライアントの初期化
azure_client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)
```

## 2. 基本的なチャット機能の実装

### 2.1 シンプルなチャット関数

```python
async def simple_chat(user_message: str, system_prompt: str = None) -> str:
    """基本的なチャット機能"""
    
    # デフォルトのシステムプロンプト
    if not system_prompt:
        system_prompt = "あなたは親切で有能な日本語のAIアシスタントです。"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    try:
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=False
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"エラー: {e}")
        return "申し訳ございません。エラーが発生しました。"
```

### 2.2 会話履歴を保持するチャット

```python
class ChatManager:
    def __init__(self, system_prompt: str = None):
        self.messages = []
        self.system_prompt = system_prompt or "あなたは親切で有能な日本語のAIアシスタントです。"
        self.messages.append({"role": "system", "content": self.system_prompt})
    
    async def chat(self, user_message: str) -> str:
        """会話履歴を保持したチャット"""
        
        # ユーザーメッセージを追加
        self.messages.append({"role": "user", "content": user_message})
        
        try:
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
                messages=self.messages,
                temperature=0.7,
                max_tokens=2000,
                stream=False
            )
            
            assistant_message = response.choices[0].message.content
            
            # アシスタントのレスポンスを履歴に追加
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            print(f"エラー: {e}")
            return "申し訳ございません。エラーが発生しました。"
    
    def clear_history(self):
        """履歴をクリア"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
```

## 3. ストリーミング機能の実装

### 3.1 基本的なストリーミング

```python
async def stream_chat(user_message: str, system_prompt: str = None):
    """ストリーミングチャット"""
    
    if not system_prompt:
        system_prompt = "あなたは親切で有能な日本語のAIアシスタントです。"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    try:
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
            stream=True  # ストリーミングを有効化
        )
        
        # ストリーミングレスポンスを処理
        full_response = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)  # リアルタイム表示
        
        return full_response
        
    except Exception as e:
        print(f"エラー: {e}")
        return "申し訳ございません。エラーが発生しました。"
```

### 3.2 FastAPIでのストリーミング

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.post("/chat/stream")
async def stream_chat_endpoint(request: dict):
    """ストリーミングチャットのAPIエンドポイント"""
    
    user_message = request.get("message", "")
    
    async def generate_response():
        messages = [
            {"role": "system", "content": "あなたは親切で有能な日本語のAIアシスタントです。"},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = azure_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True
            )
            
            # Server-Sent Events形式で配信
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content, 'type': 'message'})}\n\n"
            
            # 完了通知
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'type': 'error'})}\n\n"
    
    return StreamingResponse(generate_response(), media_type="text/plain")
```

## 4. Function Callingの実装

### 4.1 基本的なFunction Calling

```python
def define_analysis_function():
    """分析用のFunction定義"""
    return {
        "name": "analyze_text",
        "description": "テキストを分析し、感情や意図を判定する",
        "parameters": {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"],
                    "description": "感情の分類"
                },
                "intent": {
                    "type": "string",
                    "description": "ユーザーの意図"
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "description": "信頼度"
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "重要なキーワード"
                }
            },
            "required": ["sentiment", "intent", "confidence"]
        }
    }

async def analyze_with_function_calling(text: str) -> dict:
    """Function Callingを使用したテキスト分析"""
    
    analysis_function = define_analysis_function()
    
    messages = [
        {"role": "system", "content": "あなたはテキスト分析の専門家です。"},
        {"role": "user", "content": f"以下のテキストを分析してください: {text}"}
    ]
    
    try:
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            functions=[analysis_function],
            function_call={"name": "analyze_text"},
            temperature=0.3,
            max_tokens=500
        )
        
        # Function Callの結果を処理
        function_call = response.choices[0].message.function_call
        if function_call and function_call.name == "analyze_text":
            import json
            result = json.loads(function_call.arguments)
            return result
        else:
            return {"error": "Function Callingが実行されませんでした"}
            
    except Exception as e:
        return {"error": str(e)}
```

### 4.2 複数のFunctionを定義する

```python
def define_multiple_functions():
    """複数のFunction定義"""
    return [
        {
            "name": "search_web",
            "description": "Web検索を実行する",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "検索クエリ"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        },
        {
            "name": "generate_image",
            "description": "画像を生成する",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "画像生成プロンプト"},
                    "size": {"type": "string", "enum": ["256x256", "512x512", "1024x1024"], "default": "1024x1024"}
                },
                "required": ["prompt"]
            }
        },
        {
            "name": "save_note",
            "description": "メモを保存する",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "メモのタイトル"},
                    "content": {"type": "string", "description": "メモの内容"}
                },
                "required": ["title", "content"]
            }
        }
    ]

async def smart_assistant(user_message: str) -> dict:
    """複数のFunctionを使用するスマートアシスタント"""
    
    functions = define_multiple_functions()
    
    messages = [
        {"role": "system", "content": "あなたは多機能なAIアシスタントです。適切なツールを使用して、ユーザーのリクエストに応えてください。"},
        {"role": "user", "content": user_message}
    ]
    
    try:
        response = azure_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=messages,
            functions=functions,
            function_call="auto",  # 自動的に適切なFunctionを選択
            temperature=0.3,
            max_tokens=1000
        )
        
        # Function Callの結果を処理
        function_call = response.choices[0].message.function_call
        if function_call:
            import json
            function_name = function_call.name
            arguments = json.loads(function_call.arguments)
            
            # 実際のFunction実行（この例では模擬実行）
            if function_name == "search_web":
                result = await execute_web_search(arguments)
            elif function_name == "generate_image":
                result = await execute_image_generation(arguments)
            elif function_name == "save_note":
                result = await execute_save_note(arguments)
            else:
                result = {"error": f"未知のFunction: {function_name}"}
            
            return {
                "function_used": function_name,
                "arguments": arguments,
                "result": result
            }
        else:
            # 通常の応答
            return {
                "response": response.choices[0].message.content,
                "function_used": None
            }
            
    except Exception as e:
        return {"error": str(e)}
```

## 5. 画像生成機能の実装

### 5.1 基本的な画像生成

```python
import aiohttp
import asyncio

class ImageGenerator:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_IMAGE_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_IMAGE_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    
    async def generate_image(self, prompt: str, size: str = "1024x1024") -> dict:
        """DALL-E 3を使用した画像生成"""
        
        url = f"{self.endpoint}/openai/deployments/dall-e-3/images/generations"
        
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }
        
        data = {
            "prompt": prompt,
            "size": size,
            "n": 1,
            "quality": "standard"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "image_url": result["data"][0]["url"],
                            "revised_prompt": result["data"][0].get("revised_prompt", prompt)
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

# 使用例
async def main():
    generator = ImageGenerator()
    result = await generator.generate_image("美しい桜の木がある日本庭園")
    
    if result["success"]:
        print(f"画像URL: {result['image_url']}")
        print(f"修正されたプロンプト: {result['revised_prompt']}")
    else:
        print(f"エラー: {result['error']}")

# 実行
# asyncio.run(main())
```

## 6. エラーハンドリングとリトライ機能

### 6.1 堅牢なエラーハンドリング

```python
import time
import random
from typing import Optional

class RobustLLMClient:
    def __init__(self, max_retries: int = 3):
        self.client = azure_client
        self.max_retries = max_retries
    
    async def chat_with_retry(self, messages: list, **kwargs) -> Optional[str]:
        """リトライ機能付きのチャット"""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
                    messages=messages,
                    **kwargs
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                error_type = type(e).__name__
                print(f"試行 {attempt + 1} でエラー: {error_type} - {e}")
                
                if attempt < self.max_retries - 1:
                    # 指数バックオフで待機
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"{wait_time:.2f}秒待機してリトライします...")
                    await asyncio.sleep(wait_time)
                else:
                    print("最大リトライ回数に達しました")
                    return None
        
        return None
    
    async def safe_function_call(self, messages: list, functions: list, **kwargs) -> dict:
        """安全なFunction Calling"""
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
                messages=messages,
                functions=functions,
                **kwargs
            )
            
            function_call = response.choices[0].message.function_call
            if function_call:
                import json
                try:
                    arguments = json.loads(function_call.arguments)
                    return {
                        "success": True,
                        "function_name": function_call.name,
                        "arguments": arguments
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Function引数のJSON解析に失敗しました"
                    }
            else:
                return {
                    "success": False,
                    "error": "Function Callが実行されませんでした"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

## 7. 設定管理とベストプラクティス

### 7.1 設定クラスの実装

```python
from pydantic import BaseSettings
from typing import Optional

class LLMSettings(BaseSettings):
    """LLM設定管理"""
    
    # Azure OpenAI設定
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4"
    azure_openai_api_version: str = "2025-01-01-preview"
    
    # 画像生成設定
    azure_openai_image_endpoint: Optional[str] = None
    azure_openai_image_api_key: Optional[str] = None
    
    # API設定
    default_temperature: float = 0.7
    default_max_tokens: int = 2000
    request_timeout: int = 30
    max_retries: int = 3
    
    # ログ設定
    log_level: str = "INFO"
    log_requests: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 使用例
settings = LLMSettings()
```

### 7.2 ログ設定

```python
import logging
from datetime import datetime

def setup_logging():
    """ログ設定"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('llm_app.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

def log_llm_request(prompt: str, response: str, model: str):
    """LLMリクエストをログに記録"""
    
    logger.info(f"LLM Request - Model: {model}")
    logger.info(f"Prompt: {prompt[:200]}...")  # 最初の200文字のみ
    logger.info(f"Response: {response[:200]}...")  # 最初の200文字のみ
```

## 8. フロントエンド統合

### 8.1 React/Vue.jsでの統合

```javascript
// API呼び出しクライアント
class LLMApiClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async chat(message, options = {}) {
        const response = await fetch(`${this.baseURL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                temperature: options.temperature || 0.7,
                max_tokens: options.max_tokens || 2000
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    async streamChat(message, onChunk) {
        const response = await fetch(`${this.baseURL}/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.substring(6));
                    onChunk(data);
                }
            }
        }
    }
}

// 使用例
const client = new LLMApiClient();

// 通常のチャット
const response = await client.chat("こんにちは！");
console.log(response.message);

// ストリーミングチャット
await client.streamChat("長い文章を書いてください", (data) => {
    if (data.type === 'message') {
        console.log(data.content);
    } else if (data.type === 'done') {
        console.log('完了');
    }
});
```

## 9. デプロイメントとスケーリング

### 9.1 Docker化

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  llm-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_DEPLOYMENT_NAME=${AZURE_OPENAI_DEPLOYMENT_NAME}
    volumes:
      - ./logs:/app/logs
```

### 9.2 パフォーマンスの最適化

```python
# 接続プールの使用
import asyncio
from aiohttp import ClientSession, TCPConnector

class OptimizedLLMClient:
    def __init__(self):
        self.session = None
        self.connector = TCPConnector(
            limit=100,  # 最大接続数
            limit_per_host=20,  # ホスト毎の最大接続数
            ttl_dns_cache=300,  # DNS キャッシュのTTL
            use_dns_cache=True
        )
    
    async def __aenter__(self):
        self.session = ClientSession(connector=self.connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
```

## 10. まとめ

このガイドを使用することで、以下の機能を持つLLM統合アプリケーションを構築できます：

1. **基本的なチャット機能**：Azure OpenAIを使用した対話システム
2. **ストリーミング機能**：リアルタイムでの応答配信
3. **Function Calling**：構造化されたデータ処理
4. **画像生成**：DALL-E 3を使用した画像作成
5. **エラーハンドリング**：堅牢なエラー処理とリトライ機能
6. **設定管理**：環境変数とPydanticを使用した設定管理
7. **フロントエンド統合**：JavaScript/TypeScriptでのAPI呼び出し
8. **デプロイメント**：Docker化とスケーリング対応

### 次のステップ

1. 環境変数を設定してAzure OpenAIアカウントを準備
2. 基本的なチャット機能から実装を開始
3. 必要に応じてストリーミングやFunction Callingを追加
4. エラーハンドリングとログ機能を実装
5. フロントエンドと統合してユーザーインターフェースを構築

このガイドを参考に、あなたのプロジェクトに最適なLLM統合を実装してください！