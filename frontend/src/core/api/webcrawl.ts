import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Webクロールリクエスト
export interface WebCrawlRequest {
  keywords: string[];
  original_query: string;
}

// Webクロールレスポンス
export interface WebCrawlResponse {
  success: boolean;
  search_keywords?: string[];
  sources?: Array<{
    url: string;
    title: string;
    snippet: string;
  }>;
  summary?: string;
  error?: string;
}

export const webCrawlApi = {
  /**
   * Webクロールを実行して情報を収集・要約
   */
  async crawl(request: WebCrawlRequest): Promise<WebCrawlResponse> {
    const response = await axios.post<WebCrawlResponse>(`${API_BASE_URL}/api/webcrawl/crawl`, request);
    return response.data;
  },
};