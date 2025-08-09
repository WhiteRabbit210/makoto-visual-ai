# LLM呼び出しとFunction Calling仕組み

## 概要

このプロジェクトは**Azure OpenAI**を使用して、多様なLLM機能を提供しています。主要な機能として、チャット応答、Function Calling、画像生成、エージェント協調システムがあります。

## 1. 使用しているLLMサービス

### Azure OpenAI API
- **モデル**: GPT-4 / GPT-4.1
- **API**: Azure OpenAI Service
- **ライブラリ**: `openai==1.3.0`

### 環境変数設定
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_IMAGE_ENDPOINT=https://your-image-resource.openai.azure.com/
AZURE_OPENAI_IMAGE_API_KEY=your_image_api_key
```

## 2. LLM呼び出しの実装箇所

### 2.1 チャット機能 (`/backend/api/chat.py`)

#### 基本的な呼び出し
```python
# 非ストリーミング
response = azure_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
    messages=api_messages,
    temperature=request.temperature,
    max_tokens=request.max_tokens,
    stream=False
)

# ストリーミング
response = azure_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4.1"),
    messages=api_messages,
    temperature=request.temperature,
    max_tokens=request.max_tokens,
    stream=True
)
```

#### プロンプト構造
```python
# システムプロンプト（日本語対応）
system_prompt = f"""あなたは親切で有能な日本語のAIアシスタントです。
現在の時刻は {current_time_str} です。
常に日本語で回答してください。"""

# メッセージ形式
api_messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_message},
    {"role": "assistant", "content": assistant_message}
]
```

### 2.2 Function Calling (`/backend/api/agent.py`)

#### Function定義
```python
ANALYZE_FUNCTION = {
    "name": "analyze_prompt",
    "description": "ユーザープロンプトを分析し、必要な機能を判定する",
    "parameters": {
        "type": "object",
        "properties": {
            "modes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["web", "image", "rag", "none"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "reason": {"type": "string"},
                        "search_keywords": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            "analysis": {"type": "string"}
        }
    }
}
```

#### Function Calling実行
```python
response = azure_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    messages=messages,
    functions=[ANALYZE_FUNCTION],
    function_call={"name": "analyze_prompt"},
    temperature=0.3,
    max_tokens=500
)
```

#### レスポンス処理
```python
# Function Callの結果を取得
function_call = response.choices[0].message.function_call
if function_call and function_call.name == "analyze_prompt":
    try:
        # JSON形式の引数を解析
        arguments = json.loads(function_call.arguments)
        modes = arguments.get("modes", [])
        analysis = arguments.get("analysis", "")
        
        # 結果をPydanticモデルに変換
        result = AnalyzeResponse(
            modes=[AnalyzeMode(**mode) for mode in modes],
            analysis=analysis
        )
    except json.JSONDecodeError:
        # エラーハンドリング
        result = AnalyzeResponse(modes=[], analysis="解析に失敗しました")
```

### 2.3 画像生成 (`/backend/services/image_generation_service.py`)

#### DALL-E 3 API呼び出し
```python
async def generate_image(self, prompt: str, size: str = "1024x1024") -> dict:
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
    
    async with session.post(
        generation_url,
        headers=headers,
        json=data,
        timeout=aiohttp.ClientTimeout(total=120)
    ) as response:
        if response.status == 200:
            result = await response.json()
            return result
```

### 2.4 エージェント協調システム (`/backend/AI_Agent/orchestration_planner.py`)

#### 実行計画生成
```python
response = self.azure_client.chat.completions.create(
    model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
    messages=[
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.3,
    max_tokens=2000,
    response_format={"type": "json_object"}  # JSON形式を強制
)
```

#### システムプロンプト（エージェント選択）
```python
system_prompt = """あなたは複数のエージェントを協調させる実行計画を作成するプランナーです。

利用可能なエージェント：
1. analyzer_agent - テキスト分析、感情分析
2. web_agent - Web検索、情報収集
3. image_agent - 画像生成、画像編集
4. document_agent - 文書処理、RAG検索

以下のJSON形式で実行計画を作成してください：
{
    "execution_plan": [
        {
            "agent_name": "エージェント名",
            "task_description": "実行する具体的なタスク",
            "input_data": "入力データ",
            "depends_on": ["依存するエージェント名"],
            "output_key": "結果を保存するキー"
        }
    ],
    "final_output": "最終的な出力の説明"
}
"""
```

## 3. ストリーミング機能の実装

### Server-Sent Events (SSE)
```python
async def stream_chat_response():
    async for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            yield f"data: {json.dumps({'content': content, 'type': 'message'})}\n\n"
    
    # 最終メッセージ
    yield f"data: {json.dumps({'type': 'done'})}\n\n"
```

### エージェント実行のストリーミング
```python
# エージェントの実行状況をリアルタイム送信
yield f"data: {json.dumps({
    'type': 'agent_status',
    'agent_name': agent_name,
    'status': 'running',
    'message': 'エージェントが実行中です...'
})}\n\n"

# 結果の送信
yield f"data: {json.dumps({
    'type': 'agent_result',
    'agent_name': agent_name,
    'result': result_data
})}\n\n"
```

## 4. エージェントアーキテクチャ

### 基底エージェントクラス
```python
class BaseAgent:
    def __init__(self, websocket_manager=None):
        self.websocket_manager = websocket_manager
        self.azure_client = AzureOpenAI(...)
    
    async def send_status(self, status: str, message: str):
        """実行状況をWebSocketで送信"""
        if self.websocket_manager:
            await self.websocket_manager.send_status(status, message)
    
    async def execute(self, task_description: str, input_data: dict) -> dict:
        """エージェントの実行メソッド（サブクラスで実装）"""
        raise NotImplementedError
```

### 具体的エージェントの実装例
```python
class ImageAgent(BaseAgent):
    async def execute(self, task_description: str, input_data: dict) -> dict:
        await self.send_status("running", "画像生成を開始します...")
        
        # 画像生成の実行
        result = await self.generate_image(input_data.get("prompt"))
        
        await self.send_status("completed", "画像生成が完了しました")
        return {"image_url": result["url"]}
```

## 5. エラーハンドリングとフォールバック

### APIエラーのハンドリング
```python
try:
    response = azure_client.chat.completions.create(...)
except openai.APIError as e:
    logger.error(f"OpenAI API error: {e}")
    return {"error": "API呼び出しに失敗しました"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"error": "予期しないエラーが発生しました"}
```

### Function Callingのフォールバック
```python
# Function Callが失敗した場合のデフォルト動作
if not function_call or function_call.name != "analyze_prompt":
    return AnalyzeResponse(
        modes=[AnalyzeMode(type="none", confidence=0.5, reason="分析できませんでした")],
        analysis="デフォルトの分析結果"
    )
```

## 6. パフォーマンスの最適化

### 非同期処理
```python
# 複数のエージェントを並行実行
async def execute_parallel_agents(agents_tasks):
    tasks = [agent.execute(task) for agent, task in agents_tasks]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### キャッシュ機能
```python
# レスポンスのキャッシュ（将来の実装予定）
@lru_cache(maxsize=100)
def get_cached_response(prompt_hash: str):
    # キャッシュされたレスポンスを返す
    pass
```

## 7. ログとモニタリング

### 実行ログの記録
```python
import logging

logger = logging.getLogger(__name__)

# LLM呼び出しのログ
logger.info(f"LLM request: model={model}, tokens={max_tokens}")
logger.info(f"LLM response: usage={response.usage}")

# Function Callingのログ
logger.info(f"Function call: {function_call.name}")
logger.info(f"Function arguments: {function_call.arguments}")
```

### WebSocketでのリアルタイム監視
```python
# エージェントの実行状況をリアルタイム配信
await websocket_manager.send_status({
    "type": "agent_execution",
    "agent_name": agent_name,
    "status": "running",
    "timestamp": datetime.now().isoformat()
})
```

## 8. 設定とカスタマイズ

### モデルパラメータの調整
```python
# チャット用設定
chat_config = {
    "temperature": 0.7,      # 創造性レベル
    "max_tokens": 2000,      # 最大トークン数
    "top_p": 0.95,          # 多様性制御
    "frequency_penalty": 0,  # 繰り返し抑制
    "presence_penalty": 0    # 新しい話題の促進
}

# Function Calling用設定
function_config = {
    "temperature": 0.3,      # 低い値で一貫性を重視
    "max_tokens": 500,       # 短い応答
    "top_p": 0.8            # 予測可能性重視
}
```

### システムプロンプトのカスタマイズ
```python
# 日本語対応のシステムプロンプト
SYSTEM_PROMPTS = {
    "chat": "あなたは親切で有能な日本語のAIアシスタントです。",
    "analysis": "あなたは正確な分析を行う専門家です。",
    "creative": "あなたは創造的で革新的なアイデアを提供します。"
}
```

## 9. 今後の拡張計画

### 新しいLLMサービスの追加
```python
# 将来的なマルチLLM対応
class LLMRouter:
    def __init__(self):
        self.azure_client = AzureOpenAI(...)
        self.openai_client = OpenAI(...)
        self.claude_client = Anthropic(...)
    
    async def route_request(self, request_type: str, prompt: str):
        if request_type == "creative":
            return await self.claude_client.complete(prompt)
        elif request_type == "analysis":
            return await self.azure_client.chat.completions.create(...)
```

### 高度なFunction Callingの実装
```python
# 複数のFunctionを同時に呼び出す
functions = [
    search_function,
    analyze_function,
    generate_function
]

response = azure_client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    functions=functions,
    function_call="auto"  # 自動選択
)
```

## まとめ

このプロジェクトのLLM統合は以下の特徴を持ちます：

1. **包括的なLLM機能**: チャット、Function Calling、画像生成、エージェント協調
2. **高性能なストリーミング**: リアルタイムでの結果配信
3. **堅牢なエラーハンドリング**: 複数レベルでのエラー処理
4. **スケーラブルなアーキテクチャ**: プラグイン形式でのエージェント管理
5. **日本語対応**: 完全な日本語サポート

すべてのLLM呼び出しは適切に設計され、実用的なアプリケーションとして動作します。