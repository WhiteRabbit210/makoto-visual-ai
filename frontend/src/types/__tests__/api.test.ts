/**
 * API型定義のテスト
 * 
 * 型定義が正しく機能することを確認するテスト
 */

import {
  // 基本型
  UUID,
  DateTime,
  MessageRole,
  ChatMode,
  
  // チャット関連
  ChatRoom,
  ChatMessage,
  RAGContext,
  FileAttachment,
  AgentInfo,
  GetChatsParams,
  GetChatsResponse,
  CreateChatRequest,
  CreateChatResponse,
  ChatStreamRequest,
  
  // SSE関連
  TextChunkEvent,
  ImageGeneratingEvent,
  ImageGeneratedEvent,
  StreamErrorEvent,
  StreamCompleteEvent,
  
  // エージェント関連
  AgentStatusMessage,
  ModeAnalysis,
  AnalyzeRequest,
  AnalyzeResponse,
  AnalyzeContext,
  
  // ライブラリ関連
  Library,
  LibraryStatus,
  VisibilityType,
  LibraryVisibility,
  GetLibrariesParams,
  GetLibrariesResponse,
  
  // タスク関連
  Task,
  TaskCategory,
  ExecutionMode,
  TaskStatus,
  ModelSettings,
  TaskParameter,
  ParameterValidation,
  TaskVisibility,
  
  // 画像生成関連
  ImageGenerationRequest,
  ImageGenerationResponse,
  GeneratedImageData,
  ImageSize,
  ImageQuality,
  ImageStyle,
  ImageGenerationStatus,
  
  // Webクロール関連
  WebCrawlRequest,
  WebCrawlResponse,
  CrawlResult,
  CrawlJobType,
  CrawlJobStatus
} from '../api';

describe('API型定義テスト', () => {
  
  describe('基本型', () => {
    it('UUID型が文字列として扱える', () => {
      const id: UUID = 'uuid-123';
      expect(typeof id).toBe('string');
    });
    
    it('DateTime型がISO 8601形式の文字列として扱える', () => {
      const now: DateTime = new Date().toISOString();
      expect(typeof now).toBe('string');
      expect(now).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });
    
    it('MessageRole型が正しい値を受け入れる', () => {
      const roles: MessageRole[] = ['user', 'assistant', 'system'];
      roles.forEach(role => {
        expect(['user', 'assistant', 'system']).toContain(role);
      });
    });
    
    it('ChatMode型が正しい値を受け入れる', () => {
      const modes: ChatMode[] = ['chat', 'image', 'web', 'rag'];
      modes.forEach(mode => {
        expect(['chat', 'image', 'web', 'rag']).toContain(mode);
      });
    });
  });
  
  describe('チャット関連型', () => {
    it('ChatRoomが必須フィールドを持つ', () => {
      const room: ChatRoom = {
        room_id: 'room-001',
        user_id: 'user-001',
        title: 'Test Chat',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 10
      };
      
      expect(room.room_id).toBeDefined();
      expect(room.user_id).toBeDefined();
      expect(room.title).toBeDefined();
    });
    
    it('ChatMessageがtextフィールドを持つ（contentではない）', () => {
      const message: ChatMessage = {
        message_id: 'msg-001',
        user_id: 'user-001',
        room_id: 'room-001',
        timestamp: new Date().toISOString(),
        role: 'user',
        text: 'こんにちは'  // textフィールド（ドキュメント準拠）
      };
      
      expect(message.text).toBe('こんにちは');
      // @ts-expect-error - contentフィールドは存在しない
      expect(message.content).toBeUndefined();
    });
    
    it('RAGContextが正しい構造を持つ', () => {
      const context: RAGContext = {
        rag_sources: [
          {
            title: 'Document 1',
            source: 'source.pdf',
            text: 'Sample text',
            score: 0.95
          }
        ]
      };
      
      expect(context.rag_sources).toHaveLength(1);
      expect(context.rag_sources[0].score).toBeGreaterThanOrEqual(0);
      expect(context.rag_sources[0].score).toBeLessThanOrEqual(1);
    });
    
    it('FileAttachmentが正しい型を持つ', () => {
      const attachment: FileAttachment = {
        type: 'image',
        url: 'https://example.com/image.png',
        thumbnail: 'https://example.com/thumb.png',
        name: 'image.png',
        size: 1024
      };
      
      expect(['image', 'pdf', 'document', 'audio', 'video']).toContain(attachment.type);
      expect(attachment.url).toBeDefined();
    });
  });
  
  describe('SSEイベント型', () => {
    it('TextChunkEventが正しい構造を持つ', () => {
      const event: TextChunkEvent = {
        type: 'text',
        content: 'Hello, world!'
      };
      
      expect(event.type).toBe('text');
      expect(event.content).toBeDefined();
    });
    
    it('ImageGeneratedEventが画像配列を持つ', () => {
      const event: ImageGeneratedEvent = {
        type: 'images',
        images: [
          {
            url: 'https://example.com/image.png',
            prompt: 'A beautiful sunset'
          }
        ]
      };
      
      expect(event.type).toBe('images');
      expect(event.images).toHaveLength(1);
      expect(event.images[0].url).toBeDefined();
      expect(event.images[0].prompt).toBeDefined();
    });
    
    it('StreamCompleteEventが完了情報を持つ', () => {
      const event: StreamCompleteEvent = {
        type: 'done',
        done: true,
        chat_id: 'chat-001',
        message_id: 'msg-001'
      };
      
      expect(event.done).toBe(true);
      expect(event.chat_id).toBeDefined();
      expect(event.message_id).toBeDefined();
    });
  });
  
  describe('分析コンテキスト型', () => {
    it('AnalyzeContextが具体的な型を持つ', () => {
      const context: AnalyzeContext = {
        type: 'document',
        content: 'Document content',
        metadata: {
          author: 'John Doe',
          date: '2024-01-01'
        }
      };
      
      expect(context.type).toBeDefined();
      expect(context.content).toBeDefined();
      expect(context.metadata).toBeDefined();
    });
    
    it('AnalyzeRequestがAnalyzeContext配列を受け入れる', () => {
      const request: AnalyzeRequest = {
        prompt: 'Analyze this',
        context: [
          {
            type: 'document',
            content: 'Content 1'
          },
          {
            type: 'code',
            content: 'const x = 1;',
            metadata: { language: 'javascript' }
          }
        ]
      };
      
      expect(request.context).toHaveLength(2);
      expect(request.context![0].type).toBe('document');
    });
  });
  
  describe('タスクパラメータ型', () => {
    it('ParameterValidationが具体的な型を持つ', () => {
      const validation: ParameterValidation = {
        min: 0,
        max: 100,
        pattern: '^[a-zA-Z]+$',
        options: ['option1', 'option2'],
        required: true
      };
      
      expect(validation.min).toBeDefined();
      expect(validation.max).toBeDefined();
      expect(validation.pattern).toBeDefined();
      expect(validation.options).toHaveLength(2);
    });
    
    it('TaskParameterが型安全なdefault_valueを持つ', () => {
      const param1: TaskParameter = {
        parameter_id: 'param1',
        name: 'name',
        label: 'Name',
        type: 'text',
        required: true,
        default_value: 'default text',
        validation: { pattern: '^[a-zA-Z]+$' },
        ui_type: 'input',
        display_order: 1
      };
      
      const param2: TaskParameter = {
        parameter_id: 'param2',
        name: 'count',
        label: 'Count',
        type: 'number',
        required: false,
        default_value: 10,
        validation: { min: 0, max: 100 },
        ui_type: 'number',
        display_order: 2
      };
      
      expect(typeof param1.default_value).toBe('string');
      expect(typeof param2.default_value).toBe('number');
    });
  });
  
  describe('Webクロール型', () => {
    it('CrawlResultが具体的な型を持つ', () => {
      const result: CrawlResult = {
        url: 'https://example.com',
        title: 'Example Page',
        content: 'Page content',
        images: ['image1.png', 'image2.png'],
        links: ['link1.html', 'link2.html']
      };
      
      expect(result.url).toBeDefined();
      expect(result.title).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.images).toHaveLength(2);
      expect(result.links).toHaveLength(2);
    });
    
    it('WebCrawlResponseがCrawlResult配列を持つ', () => {
      const response: WebCrawlResponse = {
        job_id: 'job-001',
        status: 'completed',
        results: [
          {
            url: 'https://example.com',
            title: 'Example',
            content: 'Content'
          }
        ]
      };
      
      expect(response.results).toHaveLength(1);
      expect(response.results![0].url).toBeDefined();
    });
  });
  
  describe('型の互換性', () => {
    it('フロントエンドとバックエンドで同じフィールド名を使用', () => {
      // ChatMessage.text（contentではない）
      const message: ChatMessage = {
        message_id: 'msg-001',
        user_id: 'user-001',
        room_id: 'room-001',
        timestamp: new Date().toISOString(),
        role: 'user',
        content: 'Test message'
      };
      expect(message.content).toBeDefined();
      
      // GeneratedImageData.metadata（具体的な型）
      const imageData: GeneratedImageData = {
        image_id: 'img-001',
        url: 'https://example.com/image.png',
        revised_prompt: 'Revised prompt',
        metadata: {
          width: 1024,
          height: 1024,
          format: 'png',
          size_bytes: 1048576
        }
      };
      expect(imageData.metadata.width).toBe(1024);
      expect(imageData.metadata.format).toBe('png');
    });
  });
});