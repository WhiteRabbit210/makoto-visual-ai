# エージェントAPI型定義

## 目次

1. [概要](#概要)
2. [基本型定義](#基本型定義)
   - [AgentCapabilityDescription](#agentcapabilitydescription)
   - [ExecutionParams](#executionparams)
   - [AgentStatus](#agentstatus)
3. [オーケストレーション型定義](#オーケストレーション型定義)
   - [ExecutionPlan](#executionplan)
   - [ExecutionStep](#executionstep)
   - [StepResult](#stepresult)
4. [エージェント実行API](#エージェント実行api)
   - [ExecuteWithAgentRequest](#executewithagentrequest)
   - [AgentStatusEvent](#agentstatusevent)
   - [AgentResultEvent](#agentresultevent)
5. [プランニングAPI](#プランニングapi)
   - [CreateExecutionPlanRequest](#createexecutionplanrequest)
   - [CreateExecutionPlanResponse](#createexecutionplanresponse)
6. [エージェント管理API](#エージェント管理api)
   - [GetAgentsResponse](#getagentsresponse)
   - [GetAgentCapabilitiesResponse](#getagentcapabilitiesresponse)
7. [エラーレスポンス](#エラーレスポンス)
8. [更新履歴](#更新履歴)

## 概要

MAKOTO Visual AIのエージェント機能で使用される型定義。LLMベースのオーケストレーション、エージェント実行、ステータス管理に関する型を定義。

本ドキュメントは実装済みのAI_Agentモジュールおよび[AI Agent LLMオーケストレーション詳細設計書](../../AI_Agent_LLMオーケストレーション詳細設計.md)に基づいて作成。

## 基本型定義

### AgentCapabilityDescription

エージェントの能力記述型（BaseAgent.get_capability_description()の戻り値）：

```typescript
interface AgentCapabilityDescription {
  // 基本情報
  name: string;                       // エージェント名
  description: string;                // エージェントの概要説明
  when_to_use: string;               // 使用すべきケースの説明
  
  // 入出力定義
  inputs: {
    required: Record<string, string>; // 必須入力パラメータ（名前: 説明）
    optional?: Record<string, string>; // オプション入力パラメータ
  };
  outputs: Record<string, string>;    // 出力内容（名前: 説明）
  
  // 実行パラメータ
  execution_params: ExecutionParams;  // 実行パラメータ定義
  
  // 制約と例
  constraints: string;                // 制約事項
  examples: string[];                // 使用例
}
```

### ExecutionParams

エージェント実行パラメータの型定義：

```typescript
interface ExecutionParams {
  // LLM設定
  llm_settings: {
    temperature?: {
      default: number;                // デフォルト値
      range: [number, number];        // 許容範囲
      description?: string;           // 説明
    };
    max_tokens?: {
      default: number;
      range: [number, number];
      description?: string;
    };
    top_p?: {
      default: number;
      range: [number, number];
      description?: string;
    };
    frequency_penalty?: {
      default: number;
      range: [number, number];
      description?: string;
    };
    presence_penalty?: {
      default: number;
      range: [number, number];
      description?: string;
    };
  };
  
  // エージェント固有設定
  agent_specific?: Record<string, {
    default?: any;                   // デフォルト値
    options?: any[];                  // 選択肢（enum型の場合）
    range?: [any, any];              // 範囲（数値型の場合）
    description?: string;             // 説明
  }>;
}
```

### AgentStatus

エージェントのステータス型定義（SSEで送信）：

```typescript
interface AgentStatusMessage {
  type: 'agent_status';                // メッセージタイプ
  content: {
    execution_id: string;              // 実行ID
    agent_type: string;                // エージェントタイプ
    status: string;                    // ステータス（analyzing, processing, complete等）
    message: string;                   // 表示メッセージ
    progress?: {
      current: number;                 // 現在のステップ
      total: number;                   // 総ステップ数
      percentage: number;              // 進捗率
    };
    details?: Record<string, any>;    // 追加の詳細情報
  };
  metadata: {
    timestamp: string;                 // ISO 8601形式のタイムスタンプ
    sequence?: number;                 // シーケンス番号
  };
}
```

注: エージェントの思考状態やストリーミング応答の詳細な型定義は[SSE仕様書](../SSE仕様書.md)を参照してください。

## エージェント思考状態

エージェントの思考プロセスを表現する状態の型定義：

```typescript
type AgentThinkingStatus = 'thinking' | 'analyzing' | 'searching' | 'crawling' | 'generating' | 'complete';
```

- `thinking`: 一般的な思考中
- `analyzing`: プロンプトを分析中
- `searching`: Web検索を実行中
- `crawling`: Webページをクロール中
- `generating`: コンテンツ（テキストまたは画像）を生成中
- `complete`: 処理完了

## オーケストレーション型定義

### ExecutionPlan

実行計画の型定義（OrchestrationPlannerの出力）：

```typescript
interface ExecutionPlan {
  // 分析結果
  analysis: string;                   // ユーザーリクエストの詳細分析
  reasoning: string;                  // エージェント選択の理由
  
  // 実行計画
  execution_plan: ExecutionStep[];    // 実行ステップの配列
  
  // 成功基準とフォールバック
  success_criteria: string;           // タスクの成功判定基準
  fallback_plan: string;             // 失敗時の代替案
  
  // メタデータ
  created_at?: string;                // 作成日時（ISO 8601）
  request?: string;                   // 元のリクエスト
}
```

### ExecutionStep

実行ステップの型定義：

```typescript
interface ExecutionStep {
  // ステップ情報
  step: number;                       // ステップ番号
  agent: string;                      // 使用するエージェント名
  purpose: string;                    // このステップの目的
  
  // 入力パラメータ
  inputs: Record<string, any>;        // エージェントへの入力
  
  // 実行パラメータ
  execution_params: {
    llm_settings?: {
      temperature?: number;           // 温度（0.0-2.0）
      max_tokens?: number;            // 最大トークン数
      top_p?: number;                 // Top-p（0.0-1.0）
      frequency_penalty?: number;     // 頻度ペナルティ（-2.0-2.0）
      presence_penalty?: number;      // 存在ペナルティ（-2.0-2.0）
    };
    agent_specific?: Record<string, any>; // エージェント固有パラメータ
  };
  
  // 実行制御
  depends_on: number[];               // 依存するステップ番号のリスト
  parallel: boolean;                  // 並列実行可能かどうか
  
  // 期待される結果
  expected_output: string;            // 期待される出力の説明
  optimization_notes: string;         // パラメータ選択の根拠
}
```

### StepResult

ステップ実行結果の型定義：

```typescript
interface StepResult {
  step: number;                       // ステップ番号
  agent: string;                      // 実行したエージェント
  status: 'success' | 'failed' | 'skipped'; // 実行結果
  
  output?: any;                       // 出力データ
  error?: {
    message: string;                  // エラーメッセージ
    details?: any;                    // 詳細情報
  };
  
  execution_time_ms?: number;         // 実行時間（ミリ秒）
  started_at: string;                 // 開始日時
  completed_at?: string;              // 完了日時
}
```

## エージェント実行API

### ExecuteWithAgentRequest

エージェント実行リクエスト（SSEストリーミング用）：

```typescript
interface ExecuteWithAgentRequest {
  // チャット基本情報
  chat_id?: string;                   // チャットID
  messages: ChatMessage[];            // メッセージ履歴
  
  // エージェント設定
  agent_mode: boolean;                // エージェントモード有効化
  agent_config?: {
    auto_orchestrate?: boolean;       // 自動オーケストレーション（デフォルト: true）
    selected_agents?: string[];       // 使用するエージェントを限定
    execution_constraints?: {
      max_steps?: number;             // 最大ステップ数
      timeout_seconds?: number;       // タイムアウト（秒）
      parallel_limit?: number;        // 並列実行数の上限
    };
    thinking_visibility?: 'full' | 'summary' | 'none'; // 思考プロセスの表示レベル
  };
  
  // ストリーミング設定
  stream: boolean;                     // SSEストリーミング有効化（必須: true）
}
```

### AgentSSEEvent

エージェントSSEイベント：

```typescript
interface AgentSSEEvent {
  type: 'agent_status' | 'execution_started' | 'step_started' | 'step_completed' | 'agent_thinking';
  content: {
    // ステータス情報
    execution_id: string;              // 実行ID
    status?: string;                   // ステータス文字列
    message?: string;                  // 表示メッセージ
    
    // 実行情報
    agent_type?: string;               // エージェントタイプ
    step?: number;                     // 現在のステップ番号
    total_steps?: number;              // 総ステップ数
    
    // 進捗情報
    progress?: {
      current: number;
      total: number;
      percentage: number;
    };
    
    // 思考プロセス（type: 'agent_thinking'の場合）
    phase?: string;                    // 思考フェーズ
    thoughts?: {
      current_analysis?: string;       // 現在の分析
      confidence?: number;             // 確信度
      visibility?: 'full' | 'summary' | 'none';
    };
    
    // 詳細情報
    details?: Record<string, any>;    // 追加情報
  };
  metadata: {
    timestamp: string;                 // タイムスタンプ
    sequence?: number;                 // シーケンス番号
  };
}
```

### AgentResultEvent

エージェント実行結果イベント：

```typescript
interface AgentResultEvent {
  type: 'agent_result';
  agent: string;                      // エージェント名
  step: number;                       // ステップ番号
  
  result: {
    // 共通結果
    success: boolean;                 // 成功フラグ
    
    // Web検索結果
    crawl_sources?: Array<{
      url: string;
      title: string;
      content: string;
      relevance_score?: number;
    }>;
    
    // 画像生成結果
    images?: Array<{
      url: string;
      prompt: string;
      metadata?: Record<string, any>;
    }>;
    
    // ドキュメント処理結果
    document_analysis?: {
      summary: string;
      key_points: string[];
      metadata?: Record<string, any>;
    };
    
    // プロンプト分析結果
    analysis?: {
      intent: string;
      recommended_modes: string[];
      confidence: number;
    };
    
    // その他の結果
    data?: any;
  };
  
  metadata?: {
    execution_time_ms: number;        // 実行時間
    tokens_used?: number;             // 使用トークン数
  };
}
```

## プランニングAPI

### CreateExecutionPlanRequest

実行計画作成リクエスト：

```typescript
interface CreateExecutionPlanRequest {
  user_request: string;                // ユーザーのリクエスト文
  
  context?: ChatMessage[];             // 会話コンテキスト
  
  constraints?: {
    max_steps?: number;                // 最大ステップ数
    excluded_agents?: string[];        // 使用しないエージェント
    preferred_agents?: string[];       // 優先的に使用するエージェント
    budget?: {
      max_tokens?: number;             // 最大トークン数
      max_cost_usd?: number;           // 最大コスト（USD）
    };
  };
  
  optimization_goals?: Array<        // 最適化目標
    'speed' |                        // 速度優先
    'accuracy' |                     // 精度優先
    'cost' |                         // コスト優先
    'comprehensive'                  // 包括性優先
  >;
}
```

### CreateExecutionPlanResponse

実行計画作成レスポンス：

```typescript
interface CreateExecutionPlanResponse {
  plan: ExecutionPlan;                // 生成された実行計画
  
  estimated_metrics?: {
    total_steps: number;               // 総ステップ数
    estimated_time_seconds: number;    // 推定実行時間
    estimated_tokens: number;          // 推定トークン数
    estimated_cost_usd: number;        // 推定コスト
  };
  
  warnings?: string[];                 // 警告メッセージ
}
```

## エージェント管理API

### GetAgentsResponse

利用可能なエージェント一覧：

```typescript
interface GetAgentsResponse {
  agents: Array<{
    name: string;                      // エージェント名
    type: string;                      // エージェントタイプ
    description: string;               // 説明
    available: boolean;                // 利用可能かどうか
    capabilities: string[];            // 主要な機能
  }>;
  
  total: number;                      // 総エージェント数
}
```

### GetAgentCapabilitiesResponse

エージェント能力詳細取得レスポンス：

```typescript
interface GetAgentCapabilitiesResponse {
  agent_name: string;                 // エージェント名
  capabilities: AgentCapabilityDescription; // 能力の詳細定義
  
  usage_stats?: {
    total_executions: number;          // 総実行回数
    success_rate: number;              // 成功率（0-100）
    average_execution_time_ms: number; // 平均実行時間
  };
}
```

## エラーレスポンス

エージェント特有のエラーレスポンス：

```typescript
interface AgentErrorResponse {
  error: {
    code: AgentErrorCode;              // エラーコード
    message: string;                   // エラーメッセージ
    details?: {
      agent?: string;                  // 関連エージェント
      step?: number;                   // エラー発生ステップ
      phase?: string;                   // エラー発生フェーズ
      suggestion?: string;              // 対処法の提案
    };
  };
  status: number;                      // HTTPステータスコード
  request_id: string;                  // リクエストID
}

enum AgentErrorCode {
  // エージェント関連
  AGENT_NOT_FOUND = 'AGENT001',
  AGENT_NOT_AVAILABLE = 'AGENT002',
  AGENT_INITIALIZATION_FAILED = 'AGENT003',
  
  // 実行計画関連
  PLAN_CREATION_FAILED = 'AGENT101',
  PLAN_VALIDATION_FAILED = 'AGENT102',
  INVALID_EXECUTION_PLAN = 'AGENT103',
  
  // 実行関連
  EXECUTION_FAILED = 'AGENT201',
  EXECUTION_TIMEOUT = 'AGENT202',
  DEPENDENCY_FAILED = 'AGENT203',
  STEP_FAILED = 'AGENT204',
  
  // パラメータ関連
  INVALID_PARAMETERS = 'AGENT301',
  PARAMETER_OUT_OF_RANGE = 'AGENT302',
  
  // リソース関連
  RATE_LIMIT_EXCEEDED = 'AGENT401',
  QUOTA_EXCEEDED = 'AGENT402',
  
  // その他
  INTERNAL_ERROR = 'AGENT500'
}
```

## パラメータ選択ガイドライン

### Temperature設定の推奨値

| タスクタイプ | 推奨値 | 理由 |
|------------|--------|------|
| 事実検索・要約 | 0.0-0.3 | 正確性と一貫性が重要 |
| 一般的な説明 | 0.3-0.7 | バランスの取れた出力 |
| 創造的な文章 | 0.7-1.2 | 多様性と創造性が必要 |
| ブレインストーミング | 1.0-1.5 | 最大限の創造性 |

### エージェント別推奨設定

#### AnalyzerAgent（プロンプト分析）
- temperature: 0.2-0.3（一貫した分析）
- max_tokens: 500-1000（簡潔な分析）

#### WebAgent（検索・クロール）
- temperature: 0.1-0.3（正確な情報収集）
- max_tokens: 1000-2000（要約の詳細度）

#### ImageAgent（画像生成）
- temperature: 0.8-1.2（創造的なプロンプト）
- max_tokens: 500-1000（プロンプト生成用）

#### DocumentAgent（文書処理）
- temperature: 0.2-0.5（正確な情報抽出）
- max_tokens: 1500-3000（詳細な分析）

## SSEメッセージ送信例

```python
# サーバー側でのSSEメッセージ送信
async def stream_agent_execution():
    # エージェント思考プロセス
    yield f"data: {json.dumps({
        'type': 'agent_thinking',
        'content': {
            'execution_id': 'exec_123',
            'agent_type': 'OrchestrationPlanner',
            'phase': 'analyzing',
            'thoughts': {
                'current_analysis': 'ユーザーリクエストを分析中',
                'confidence': 0.85,
                'visibility': 'summary'
            }
        },
        'metadata': {
            'timestamp': datetime.now().isoformat()
        }
    })}\n\n"
    
    # ステップ完了
    yield f"data: {json.dumps({
        'type': 'step_completed',
        'content': {
            'execution_id': 'exec_123',
            'step': 1,
            'agent': 'WebAgent',
            'status': 'success'
        },
        'metadata': {
            'timestamp': datetime.now().isoformat()
        }
    })}\n\n"
    
    # 完了シグナル
    yield "data: [DONE]\n\n"
```

## 更新履歴

- 2025-08-06: 初版作成
  - 実装済みのAI_Agentモジュールに基づく型定義
  - LLMベースオーケストレーション機能
  - WebSocketからSSEへの変更
  - 実行計画の作成と実行