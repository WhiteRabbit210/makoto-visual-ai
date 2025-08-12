import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export interface TaskTemplate {
  id: string;
  name: string;
  description: string;
  prompt: string;
  category: string;
  created_at: string;
  updated_at: string;
}

export const taskTemplatesApi = {
  // 全タスクテンプレート取得
  async getAllTemplates(): Promise<TaskTemplate[]> {
    const response = await axios.get(`${API_BASE_URL}/api/task-templates`);
    return response.data;
  },

  // 特定のタスクテンプレート取得
  async getTemplateById(id: string): Promise<TaskTemplate> {
    const response = await axios.get(`${API_BASE_URL}/api/task-templates/${id}`);
    return response.data;
  },

  // カテゴリー別タスクテンプレート取得
  async getTemplatesByCategory(category: string): Promise<TaskTemplate[]> {
    const response = await axios.get(`${API_BASE_URL}/api/task-templates/category/${category}`);
    return response.data;
  }
};