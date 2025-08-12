import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import { MessageActions } from './MessageActions';
import { MessageAvatar } from './MessageAvatar';
import { PDFViewer } from '../../../../shared/components/PDFViewer';
import { MessageItemSkeleton } from '../MessageList/MessageItemSkeleton';
import { ImageGeneratingIndicator } from './ImageGeneratingIndicator';

interface PDFSource {
  id: string;
  title: string;
  url: string;
  pages: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: PDFSource[];
  images?: Array<{
    url: string;
    prompt?: string;
    created_at?: string;
  }>;
  crawl_sources?: Array<{
    url: string;
    title: string;
    snippet: string;
  }>;
}

interface MessageItemProps {
  message: Message;
  isStreaming?: boolean;
  streamingContent?: string;
  isGeneratingImage?: boolean;
}

export const MessageItem: React.FC<MessageItemProps> = ({ message, isStreaming = false, streamingContent, isGeneratingImage = false }) => {
  const isUser = message.role === 'user';
  const [feedback, setFeedback] = useState<'good' | 'bad' | null>(null);
  const [isRendered, setIsRendered] = useState(false);
  const itemRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Intersection Observerを使用して要素が実際に表示されたことを検知
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // 少し遅延を入れて描画が完了したことを確実にする
            setTimeout(() => {
              setIsRendered(true);
            }, 50);
          }
        });
      },
      { threshold: 0.1 }
    );

    if (itemRef.current) {
      observer.observe(itemRef.current);
    }

    return () => {
      if (itemRef.current) {
        observer.unobserve(itemRef.current);
      }
    };
  }, []);

  const handleFeedback = (type: 'good' | 'bad') => {
    setFeedback(type);
    // ここで実際のフィードバック送信処理を行う
    console.log(`Feedback: ${type} for message ${message.id}`);
  };

  return (
    <div ref={itemRef} className="relative">
      {/* スケルトン - フェードアウト */}
      <div
        className={`absolute inset-0 transition-opacity duration-300 ${
          isRendered ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <MessageItemSkeleton isUser={isUser} />
      </div>

      {/* 実際のメッセージ - フェードイン */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isRendered || isStreaming ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className={!isRendered && !isStreaming ? 'pointer-events-none' : ''}
      >
      <div
        className={`flex gap-2 ${isUser ? 'flex-row-reverse' : ''}`}
      >
        {/* Avatar */}
        <MessageAvatar role={message.role} />

        {/* Message Content */}
        <div className={`${isUser ? 'flex flex-col items-end ml-auto' : 'mr-auto'} max-w-[80%]`}>
          <div className="flex flex-col gap-3">
            {/* メッセージ本文 */}
            <div className="relative group inline-block">
              <MessageBubble 
                content={message.content} 
                role={message.role} 
                isStreaming={isStreaming}
                streamingContent={streamingContent}
                crawlSources={message.crawl_sources}
              />
              
              {/* Action Buttons */}
              {!isStreaming && message.content && (
                <MessageActions 
                  messageId={message.id}
                  content={message.content}
                  isUser={isUser}
                  feedback={feedback}
                  onFeedback={handleFeedback}
                />
              )}
            </div>
          </div>
          
          <p className={`text-xs text-text-muted mt-1 ${isUser ? 'text-right' : ''}`}>
            {message.timestamp}
          </p>
        </div>
      </div>
      
      {/* PDFビューア - メッセージの外側に配置 */}
      {!isUser && message.sources && message.sources.length > 0 && (
        <div className="mt-3 w-[80%] ml-[2.75rem]">
          <PDFViewer sources={message.sources} />
        </div>
      )}
      
      {/* 画像生成中インジケーター */}
      {!isUser && isStreaming && isGeneratingImage && (
        <div className="mt-3 w-[80%] ml-[2.75rem]">
          <ImageGeneratingIndicator />
        </div>
      )}
      
      {/* 生成された画像 - メッセージの外側に配置 */}
      {!isUser && message.images && message.images.length > 0 && (
        <div className="mt-3 w-[80%] ml-[2.75rem] space-y-3">
          {message.images.map((image, index) => (
            <div key={index} className="relative group">
              <img 
                src={`http://localhost:8000${image.url}`}
                alt={image.prompt || `Generated image ${index + 1}`}
                className="rounded-lg shadow-lg w-full max-w-2xl"
                loading="lazy"
              />
              {image.prompt && (
                <div className="mt-2 text-sm text-text-muted italic">
                  プロンプト: {image.prompt}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      
      </motion.div>
    </div>
  );
};