"""
エージェントAPI

ドキュメント（/makoto/docs/仕様書/型定義/エージェントAPI型定義.md）に
完全準拠した実装です。
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from openai import AzureOpenAI
import os
import json
from dotenv import load_dotenv
from utils.logger import log_api_request, log_api_response, log_error

# ドキュメント準拠の型定義をインポート
from backend_types.api_types import (
    ModeAnalysis,
    AnalyzeRequest,
    AnalyzeResponse,
    AnalyzeContext,
    AgentStatusMessage,
    AgentThinkingStatus
)

load_dotenv()

router = APIRouter()

# Azure OpenAIクライアントを初期化
try:
    # Azure OpenAI APIバージョンを取得
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # デフォルト値なし
    azure_client = AzureOpenAI(
        api_version=api_version,
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    )
    print(f"Azure OpenAI初期化成功 - API Version: {api_version}")
except Exception as e:
    print(f"Azure OpenAI設定エラー: {e}")
    azure_client = None

# Function Callingのスキーマ定義
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
                        "type": {
                            "type": "string",
                            "enum": ["web", "image", "rag", "chat", "none"],
                            "description": "有効にすべきモードのタイプ"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "判定の確信度（0-1）"
                        },
                        "reason": {
                            "type": "string",
                            "description": "このモードを選択した理由"
                        },
                        "search_keywords": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Webモードの場合のGoogle検索キーワード（3-5個）"
                        }
                    },
                    "required": ["type", "confidence", "reason"]
                }
            },
            "analysis": {
                "type": "string",
                "description": "プロンプトの全体的な分析"
            }
        },
        "required": ["modes", "analysis"]
    }
}

# エージェントのシステムプロンプト
AGENT_SYSTEM_PROMPT = """あなたはユーザーの質問を分析し、最適な回答方法を判定するAIエージェントです。

以下の基準に従って、各モードの必要性を判定してください：

## Webクロール (web)
以下の場合に有効にする：
- 最新の情報が必要な質問（ニュース、現在の出来事、最近の変更）
- 特定の企業や人物の現在の情報（社長、CEO、役員など）
- リアルタイムデータ（株価、為替、天気、スポーツの結果など）
- ナレッジカットオフ以降の情報
- 検証可能な事実確認が必要な質問
- ハルシネーションのリスクが高い具体的な事実に関する質問

Webモードを選択した場合は、必ず3-5個の具体的なGoogle検索キーワードを含めてください。
キーワードは質問の核心を捉え、効果的な検索結果が得られるように選定してください。

## 画像生成 (image)
以下の場合に有効にする：
- 画像、イラスト、図、絵の作成・生成の明示的な要求
- ビジュアル表現、デザイン、アートワークの依頼
- 「描いて」「作って」「生成して」などの画像関連の動詞が含まれる

## RAGモード (rag)
以下の場合に有効にする：
- アップロードされたドキュメントやファイルに関する質問
- 特定の文書やデータセットを参照する必要がある質問
- 「この文書で」「アップロードしたファイルの」などの参照がある

## チャットモード (chat)
以下の場合に選択：
- 対話的な応答が必要な質問
- 段階的な説明や質疑応答

## 通常モード (none)
以下の場合に選択：
- 一般的な知識で回答可能な質問
- プログラミング、コード生成、技術的な説明
- 数学的計算、論理的推論
- 創造的な文章作成（画像以外）

複数のモードが該当する場合は、すべてを含めてください。
確信度は0から1の値で表し、該当する可能性の高さを示してください。"""

@router.post("/analyze")
async def analyze_prompt(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    ユーザープロンプトを分析して必要なモードを判定
    
    ドキュメント準拠のエージェント分析API
    """
    print(f"\n=== エージェント分析リクエスト受信 ===")
    print(f"プロンプト: {request.prompt[:100]}...")
    print(f"コンテキスト数: {len(request.context) if request.context else 0}")
    
    log_api_request("/api/agent/analyze", "POST", {
        "prompt_length": len(request.prompt),
        "has_context": bool(request.context and len(request.context) > 0)
    })
    
    try:
        if not azure_client:
            raise HTTPException(status_code=500, detail="Azure OpenAIクライアントが初期化されていません")
        
        # Function Callingを使用してプロンプトを分析
        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"次のプロンプトを分析してください：\n\n{request.prompt}"}
        ]
        
        # コンテキストがある場合は追加
        if request.context:
            context_str = "\n".join([
                f"{ctx.type}: {ctx.content[:100]}..." 
                for ctx in request.context[-3:]
            ])
            messages.insert(1, {
                "role": "system", 
                "content": f"過去のコンテキスト：\n{context_str}"
            })
        
        # モデル名を取得
        # GPT-5に問題があるため、一時的にGPT-4.1を使用
        model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # GPT-5とGPT-4で異なるパラメータを使用
        # 現在はGPT-5を無効化してGPT-4.1を使用
        if "gpt-5" in model_name.lower() and False:  # GPT-5は一時的に無効化
            # GPT-5の場合はJSONモードを使用（Function Callingが動作しないため）
            json_schema = json.dumps(ANALYZE_FUNCTION["parameters"], ensure_ascii=False, indent=2)
            
            # システムプロンプトにJSON出力を指示
            json_messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT + f"\n\n必ず以下のJSON形式で回答してください：\n{json_schema}"},
                {"role": "user", "content": f"次のプロンプトを分析してJSON形式で回答してください：\n\n{request.prompt}"}
            ]
            
            # コンテキストがある場合は追加
            if request.context:
                context_str = "\n".join([
                    f"{ctx.type}: {ctx.content[:100]}..." 
                    for ctx in request.context[-3:]
                ])
                json_messages.insert(1, {
                    "role": "system", 
                    "content": f"過去のコンテキスト：\n{context_str}"
                })
            
            response = azure_client.chat.completions.create(
                model=model_name,
                messages=json_messages,
                # response_format={"type": "json_object"},  # GPT-5では動作しない可能性
                # temperature=0.3,  # GPT-5はデフォルト値(1)のみサポート
                max_completion_tokens=1000  # 出力トークン数を増やす
            )
            
            # GPT-5の場合は通常のcontentをJSONとしてパース
            response_message = response.choices[0].message
            print(f"GPT-5レスポンス（JSONモード）: {response_message.content}")
            
            try:
                # GPT-5のレスポンスから改行や制御文字を処理
                content = response_message.content
                # 不完全なJSONの場合、閉じ括弧を追加する応急処置
                if content.count("{") > content.count("}"):
                    content += '"}]}'  # 不足している閉じ括弧を追加
                
                result = json.loads(content)
                print(f"パース結果: {result}")
                
                # GPT-5が返す構造を確認して適切に処理
                if "properties" in result and isinstance(result["properties"], dict):
                    # スキーマ形式で返された場合
                    actual_data = result["properties"]
                    modes = [ModeAnalysis(**mode) for mode in actual_data.get("modes", [])]
                    if "analysis" not in actual_data:
                        actual_data["analysis"] = "プロンプトを分析しました"
                    result = actual_data
                else:
                    # 正しい形式で返された場合
                    modes = [ModeAnalysis(**mode) for mode in result.get("modes", [])]
                    if "analysis" not in result:
                        result["analysis"] = "プロンプトを分析しました"
                    
            except json.JSONDecodeError as parse_error:
                print(f"JSONパースエラー: {parse_error}")
                print(f"レスポンス内容: {response_message.content}")
                # フォールバック：デフォルトの応答を返す
                modes = [ModeAnalysis(type="chat", confidence=0.8, reason="JSONパースエラーのためチャットモードを選択")]
                result = {"analysis": "分析中にエラーが発生しました"}
                
        else:
            # GPT-4.1では functions パラメータを使用（従来の方式）
            # 現在はこちらのブランチが実行される
            response = azure_client.chat.completions.create(
                model=model_name,
                messages=messages,
                functions=[ANALYZE_FUNCTION],
                function_call={"name": "analyze_prompt"},
                temperature=0.3,  # GPT-4.1では温度調整可能
                max_tokens=500  # GPT-4.1ではmax_tokensを使用
            )
            
            # Function Callの結果を解析
            function_call = response.choices[0].message.function_call
            print(f"Function Call結果: {function_call}")
            
            if function_call and function_call.name == "analyze_prompt":
                try:
                    result = json.loads(function_call.arguments)
                    print(f"パース結果: {result}")
                    
                    # レスポンスモデルに変換
                    modes = [ModeAnalysis(**mode) for mode in result["modes"]]
                except Exception as parse_error:
                    print(f"パースエラー: {parse_error}")
                    print(f"Function Call Arguments: {function_call.arguments}")
                    raise
            else:
                raise HTTPException(status_code=500, detail="Function Callの結果が期待した形式ではありません")
        
        # 最も確信度の高いモードを選択
        primary_mode = None
        if modes:
            # confidence > 0.5 のモードの中で最も高いものを選択
            high_confidence_modes = [m for m in modes if m.confidence > 0.5]
            if high_confidence_modes:
                primary_mode = max(high_confidence_modes, key=lambda m: m.confidence).type
            
        response_data = AnalyzeResponse(
            modes=modes,
            analysis=result["analysis"],
            primary_mode=primary_mode
        )
        
        log_api_response("/api/agent/analyze", 200, {
            "modes_count": len(modes),
            "primary_mode": primary_mode
        })
        
        return response_data
            
    except Exception as e:
        log_error("Agent Analysis Error", str(e), "/api/agent/analyze")
        raise HTTPException(status_code=500, detail=f"エージェント分析エラー: {str(e)}")

@router.post("/status")
async def send_agent_status(status: AgentStatusMessage):
    """
    エージェントのステータスを送信
    
    エージェントの実行状況をクライアントに通知します
    """
    log_api_request("/api/agent/status", "POST", {
        "execution_id": status.content.execution_id,
        "agent_type": status.content.agent_type,
        "status": status.content.status
    })
    
    # ここでSSEやWebSocketを使ってクライアントに通知する実装を追加
    # 現在は単純にレスポンスを返すのみ
    
    log_api_response("/api/agent/status", 200, {
        "status_sent": True
    })
    
    return {"success": True, "message": "Status sent"}

@router.get("/thinking/{execution_id}")
async def get_thinking_status(execution_id: str) -> dict:
    """
    エージェントの思考状態を取得
    
    指定された実行IDのエージェントの現在の思考状態を返します
    """
    # 実際の実装では、実行IDに基づいて状態を管理する必要があります
    # ここではモック実装
    
    log_api_request("/api/agent/thinking", "GET", {
        "execution_id": execution_id
    })
    
    # モックレスポンス
    thinking_status: AgentThinkingStatus = "analyzing"
    
    log_api_response("/api/agent/thinking", 200, {
        "execution_id": execution_id,
        "status": thinking_status
    })
    
    return {
        "execution_id": execution_id,
        "status": thinking_status,
        "message": "プロンプトを分析中..."
    }