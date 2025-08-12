import React, { useRef, useEffect } from 'react';
import { FileReferenceTag } from './FileReferenceTag';

interface RichTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  fileReferences: Map<string, File>;
  disabled?: boolean;
  placeholder?: string;
}

export const RichTextarea: React.FC<RichTextareaProps> = ({
  value,
  onChange,
  onKeyPress,
  fileReferences,
  disabled = false,
  placeholder = "メッセージを入力..."
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const previewRef = useRef<HTMLDivElement>(null);
  const isComposingRef = useRef(false);

  // テキストエリアの高さを自動調整
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(Math.max(scrollHeight, 44), 200) + 'px';
    }
  }, [value]);

  // リッチコンテンツをレンダリング
  const renderRichContent = () => {
    if (!value) return null;

    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    
    // ファイル参照パターンを検索 [filename.ext]
    const pattern = /\[([^\]]+)\]/g;
    let match;
    
    while ((match = pattern.exec(value)) !== null) {
      // マッチ前のテキスト
      if (match.index > lastIndex) {
        parts.push(
          <span key={`text-${lastIndex}`}>
            {value.substring(lastIndex, match.index)}
          </span>
        );
      }
      
      // ファイル参照
      const fileName = match[1];
      const file = fileReferences.get(fileName);
      if (file) {
        parts.push(
          <FileReferenceTag
            key={`file-${fileName}-${match.index}`}
            fileName={fileName}
            fileType={file.type}
          />
        );
      } else {
        // ファイルが見つからない場合は通常のテキストとして表示
        parts.push(
          <span key={`text-${match.index}`}>
            {match[0]}
          </span>
        );
      }
      
      lastIndex = match.index + match[0].length;
    }
    
    // 残りのテキスト
    if (lastIndex < value.length) {
      parts.push(
        <span key={`text-end-${lastIndex}`}>
          {value.substring(lastIndex)}
        </span>
      );
    }
    
    return parts;
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // 日本語入力中はEnterキーでの送信を無効化
    if (e.key === 'Enter' && !e.shiftKey && !isComposingRef.current) {
      e.preventDefault();
      onKeyPress(e);
    }
  };

  const handleCompositionStart = () => {
    isComposingRef.current = true;
  };

  const handleCompositionEnd = () => {
    isComposingRef.current = false;
  };

  return (
    <div className="relative">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        onCompositionStart={handleCompositionStart}
        onCompositionEnd={handleCompositionEnd}
        disabled={disabled}
        placeholder={placeholder}
        className="w-full p-3 pr-12 bg-bg-secondary border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue/30 transition-all scrollbar-thin overflow-y-auto text-transparent caret-text-primary"
        style={{ minHeight: '44px' }}
      />
      
      {/* リッチコンテンツオーバーレイ */}
      <div 
        ref={previewRef}
        className="absolute inset-0 p-3 pr-12 pointer-events-none overflow-hidden"
        style={{ 
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap'
        }}
      >
        {renderRichContent()}
        {!value && (
          <span className="text-text-muted/50">{placeholder}</span>
        )}
      </div>
    </div>
  );
};