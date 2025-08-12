// 共通の型定義
export interface User {
  id: string;
  name: string;
  email?: string;
  avatar?: string;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

export interface PaginationParams {
  page: number;
  limit: number;
  total?: number;
}