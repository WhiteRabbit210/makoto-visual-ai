import React, { useRef, useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { MessageItem } from '../MessageItem';
import { MessageItemSkeleton } from './MessageItemSkeleton';
import { AgentThinking } from '../AgentThinking';
import { AgentThought } from '../MessageItem';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Array<{
    id: string;
    title: string;
    url: string;
    pages: number;
  }>;
}

interface AgentThoughtMessage {
  id: string;
  role: 'agent_thought';
  content: string;
  timestamp: string;
  status?: 'thinking' | 'analyzing' | 'searching' | 'crawling' | 'generating' | 'complete';
}

interface MessageListProps {
  messages: (Message | AgentThoughtMessage)[];
  isLoading: boolean;
  isChangingChat: boolean;
  activeChat: string | null;
  lastUserMessageId?: string;
  streamingContent?: string;
  isStreaming?: boolean;
  isGeneratingImage?: boolean;
  isAgentThinking?: boolean;
  agentAnalysisResult?: {
    modes: Array<{
      type: string;
      confidence: number;
      reason: string;
      search_keywords?: string[];
    }>;
    analysis: string;
    primary_mode?: string;
  };
  agentThinkingStatus?: 'analyzing' | 'searching' | 'crawling' | 'generating';
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  isChangingChat,
  activeChat,
  lastUserMessageId,
  streamingContent,
  isStreaming = false,
  isGeneratingImage = false,
  isAgentThinking = false,
  agentAnalysisResult,
  agentThinkingStatus = 'analyzing',
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const lastUserMessageRef = useRef<HTMLDivElement>(null);
  const [shouldScrollToUser, setShouldScrollToUser] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToLastUserMessage = () => {
    if (lastUserMessageRef.current) {
      lastUserMessageRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      });
    }
  };

  // 新しいユーザーメッセージが送信された時の処理
  useEffect(() => {
    if (lastUserMessageId && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'user' && lastMessage.id === lastUserMessageId) {
        setShouldScrollToUser(true);
        setTimeout(() => {
          scrollToLastUserMessage();
          setShouldScrollToUser(false);
        }, 100);
      }
    }
  }, [lastUserMessageId, messages]);

  // AI応答中またはストリーミング中の自動スクロール
  useEffect(() => {
    if (isLoading || !shouldScrollToUser) {
      scrollToBottom();
    }
  }, [messages, isLoading, shouldScrollToUser]);

  return (
    <div ref={containerRef} className="flex-1 overflow-y-auto scrollbar-thin px-4 py-4">
      <AnimatePresence mode="wait">
        {!isChangingChat && (
          <motion.div
            key={activeChat}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="w-full space-y-4"
          >
            {/* メッセージがない場合の表示 */}
            {messages.length === 0 && !isChangingChat && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full text-center text-text-muted py-20">
                <p className="text-lg mb-2">こちらは新しいチャットです</p>
                <p className="text-sm">メッセージを入力して会話を始めてください</p>
              </div>
            )}
            
            {/* 初回読み込み時のスケルトン表示 */}
            {messages.length === 0 && isChangingChat && (
              <>
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={`skeleton-${i}`}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="mb-4"
                  >
                    <MessageItemSkeleton isUser={i % 2 === 0} />
                  </motion.div>
                ))}
              </>
            )}
            
            {messages.map((message, index) => {
              const isLastUserMessage = message.role === 'user' && message.id === lastUserMessageId;
              
              // エージェントの思考メッセージの場合
              if (message.role === 'agent_thought') {
                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <AgentThought 
                      content={message.content} 
                      timestamp={message.timestamp}
                      status={message.status}
                    />
                  </motion.div>
                );
              }
              
              // 通常のメッセージ
              return (
                <motion.div
                  key={message.id}
                  ref={isLastUserMessage ? lastUserMessageRef : undefined}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <MessageItem message={message as Message} />
                </motion.div>
              );
            })}
            
            {/* エージェント思考中表示 */}
            <AgentThinking 
              isVisible={isAgentThinking} 
              status={agentThinkingStatus}
              details={agentAnalysisResult ? `分析完了: ${agentAnalysisResult.modes?.map((m) => `${m.type} (${Math.round(m.confidence * 100)}%)`).join(', ')}` : undefined}
            />
            {isLoading && (
              <MessageItem
                message={{
                  id: 'streaming',
                  role: 'assistant',
                  content: streamingContent || '',
                  timestamp: new Date().toLocaleString('ja-JP'),
                }}
                isStreaming={isStreaming}
                streamingContent={streamingContent}
                isGeneratingImage={isGeneratingImage}
              />
            )}
            {/* 大きなスペースを確保してスクロールを楽にする */}
            <div className="h-96" />
            <div ref={messagesEndRef} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};