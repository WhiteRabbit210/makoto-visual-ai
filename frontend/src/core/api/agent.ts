import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// エージェント分析のモード
export interface ModeAnalysis {
  type: 'web' | 'image' | 'rag' | 'none';
  confidence: number;
  reason: string;
  search_keywords?: string[];  // Webモード時のGoogle検索キーワード
}

// エージェント分析リクエスト
export interface AnalyzeRequest {
  prompt: string;
  context?: Array<{
    role: string;
    content: string;
  }>;
}

// エージェント分析レスポンス
export interface AnalyzeResponse {
  modes: ModeAnalysis[];
  analysis: string;
  primary_mode?: string;
}

export const agentApi = {
  /**
   * プロンプトを分析して最適なモードを判定
   */
  async analyzePrompt(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    const response = await axios.post<AnalyzeResponse>(`${API_BASE_URL}/api/agent/analyze`, request);
    return response.data;
  },
};