import axios from 'axios';
import type { 
  ChatRoom, 
  GetChatsResponse
} from '../../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const chatApi = {
  /**
   * チャット一覧を取得（ページネーション対応）
   */
  async getChats(offset: number = 0, limit: number = 20): Promise<GetChatsResponse> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chats`, {
        params: { offset, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Get chats error:', error);
      throw error;
    }
  },

  /**
   * 特定のチャットを取得
   */
  async getChat(chatId: string): Promise<ChatRoom> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/chats/${chatId}`);
      return response.data;
    } catch (error) {
      console.error('Get chat error:', error);
      throw error;
    }
  },

  /**
   * チャットを削除
   */
  async deleteChat(chatId: string): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/api/chats/${chatId}`);
    } catch (error) {
      console.error('Delete chat error:', error);
      throw error;
    }
  }
};