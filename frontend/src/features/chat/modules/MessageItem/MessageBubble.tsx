import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  content: string;
  role: 'user' | 'assistant';
  isStreaming?: boolean;
  streamingContent?: string;
  crawlSources?: Array<{
    url: string;
    title: string;
    snippet: string;
  }>;
}

export const MessageBubble: React.FC<MessageBubbleProps> = React.memo(({ content, role, isStreaming = false, streamingContent, crawlSources }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`
      px-4 py-3 rounded-xl border
      ${isUser 
        ? 'bg-primary-blue/5 border-primary-blue/20 text-text-primary' 
        : 'bg-white border-border'
      }
    `}>
      {isUser ? (
        <p className="whitespace-pre-wrap">
          {content}
        </p>
      ) : (
        <div className="prose prose-sm max-w-none
          prose-p:mt-0 prose-p:mb-3 prose-p:last:mb-0
          prose-headings:mt-4 prose-headings:mb-2
          prose-h1:text-lg prose-h2:text-base prose-h3:text-sm
          prose-strong:text-text-primary
          prose-ul:my-2 prose-ol:my-2
          prose-li:my-0.5
          prose-blockquote:border-l-primary-blue prose-blockquote:bg-primary-blue/5
          prose-code:bg-bg-tertiary prose-code:px-1 prose-code:py-0.5 prose-code:rounded
          prose-pre:bg-bg-tertiary prose-pre:border prose-pre:border-border
        ">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              p: ({children}) => <p className="leading-relaxed">{children}</p>,
              code(props) {
                const {inline, className, children, ...rest} = props as {node?: unknown; inline?: boolean; className?: string; children?: React.ReactNode; [key: string]: unknown};
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <pre className="overflow-x-auto bg-bg-tertiary p-3 rounded-lg border border-border">
                    <code className={className} {...rest}>
                      {String(children).replace(/\n$/, '')}
                    </code>
                  </pre>
                ) : (
                  <code className="text-sm bg-bg-tertiary px-1 py-0.5 rounded" {...rest}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {isStreaming && streamingContent ? streamingContent : content}
          </ReactMarkdown>
        </div>
      )}
      {isStreaming && (
        <span className="inline-block w-2 h-4 bg-primary-blue animate-pulse ml-1 align-middle" />
      )}
      
      {/* 参照元URLタグ */}
      {!isUser && crawlSources && crawlSources.length > 0 && (
        <div className="mt-3 pt-3 border-t border-border/30">
          <div className="flex flex-wrap gap-2">
            {crawlSources.map((source, index) => {
              // URLからドメインを抽出
              const domain = new URL(source.url).hostname.replace('www.', '');
              // タイトルを省略（30文字まで）
              const truncatedTitle = source.title.length > 30 ? source.title.substring(0, 30) + '...' : source.title;
              
              return (
                <a
                  key={index}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 px-2 py-1 bg-bg-tertiary hover:bg-bg-secondary border border-border rounded-md text-xs text-text-secondary hover:text-text-primary transition-colors group"
                  title={`${source.title}\n${source.url}`}
                >
                  <svg className="w-3 h-3 text-text-muted group-hover:text-primary transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  <span className="font-medium">{truncatedTitle}</span>
                  <span className="text-text-muted">({domain})</span>
                </a>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
});