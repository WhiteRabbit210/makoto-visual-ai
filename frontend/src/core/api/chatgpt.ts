import axios from 'axios';
import type { 
  ChatMessage,
  ChatStreamRequest,
  AgentStatusMessage 
} from '../../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// クロールソース型定義
interface CrawlSource {
  url: string;
  title: string;
  snippet: string;
}

// 生成画像型定義
interface GeneratedImage {
  url: string;
  prompt?: string;
  created_at?: string;
}

// ストリーミングコールバック型定義（型安全で再利用可能）
interface StreamingCallbacks {
  onChunk: (chunk: string) => void;
  onDone: (chatId?: string, crawlSources?: CrawlSource[]) => void;
  onImage?: (images: GeneratedImage[]) => void;
  onGeneratingImage?: () => void;
  onImageError?: (error: string) => void;
  onAgentThought?: (thought: string, status: string) => void;
  onAgentStatus?: (status: AgentStatusMessage) => void;
}

export const chatGPTApi = {
  /**
   * ChatGPTに一度にメッセージを送信して応答を取得
   */
  async sendMessage(request: ChatStreamRequest): Promise<ChatMessage> {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/completion`, request);
      return response.data;
    } catch (error) {
      console.error('ChatGPT API Error:', error);
      throw error;
    }
  },

  /**
   * ストリーミング形式でChatGPTの応答を取得
   * @param request - チャットストリーミングリクエスト
   * @param callbacks - ストリーミングイベントのコールバック関数群
   * @returns チャットID（成功時）またはundefined
   */
  async streamMessage(
    request: ChatStreamRequest,
    callbacks: StreamingCallbacks
  ): Promise<string | undefined> {
    const { onChunk, onDone, onImage, onGeneratingImage, onImageError, onAgentThought, onAgentStatus } = callbacks;
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Reader is not available');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          // 最後のデータを処理
          if (buffer.trim()) {
            const lines = buffer.split('\n');
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data.trim()) {
                  try {
                    const parsed = JSON.parse(data);
                    if (parsed.done) {
                      onDone(parsed.chat_id, parsed.crawl_sources as CrawlSource[] | undefined);
                      return;
                    } else if (parsed.content) {
                      onChunk(parsed.content);
                    } else if (parsed.type === 'agent_thought' && onAgentThought) {
                      onAgentThought(parsed.content, parsed.status);
                    } else if (parsed.type === 'agent_status' && onAgentStatus) {
                      onAgentStatus(parsed);
                    } else if (parsed.generating_image && onGeneratingImage) {
                      onGeneratingImage();
                    } else if (parsed.images && onImage) {
                      onImage(parsed.images);
                    } else if (parsed.image_error && onImageError) {
                      onImageError(parsed.image_error);
                    }
                  } catch (e) {
                    console.error('Error parsing SSE data:', e);
                  }
                }
              }
            }
          }
          break;
        }

        const chunk = decoder.decode(value, { stream: true });
        buffer += chunk;

        // 完全な行を処理
        const lines = buffer.split('\n');
        // 最後の（おそらく不完全な）行を保持
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data.trim()) {
              try {
                const parsed = JSON.parse(data);
                if (parsed.done) {
                  onDone(parsed.chat_id, parsed.crawl_sources as CrawlSource[] | undefined);
                  return parsed.chat_id;
                } else if (parsed.content) {
                  onChunk(parsed.content);
                } else if (parsed.type === 'agent_thought' && onAgentThought) {
                  onAgentThought(parsed.content, parsed.status);
                } else if (parsed.type === 'agent_status' && onAgentStatus) {
                  onAgentStatus(parsed);
                } else if (parsed.generating_image && onGeneratingImage) {
                  onGeneratingImage();
                } else if (parsed.images && onImage) {
                  onImage(parsed.images);
                } else if (parsed.image_error && onImageError) {
                  onImageError(parsed.image_error);
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e, 'Line:', line);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('ChatGPT Streaming Error:', error);
      throw error;
    }
  }
};