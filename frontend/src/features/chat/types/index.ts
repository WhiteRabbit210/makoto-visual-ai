export interface PDFSource {
  id: string;
  title: string;
  url: string;
  pages: number;
  currentPage?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: PDFSource[];
}

export interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}