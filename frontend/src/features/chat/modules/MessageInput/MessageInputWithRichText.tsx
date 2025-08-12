import React, { useRef, useEffect, useState } from 'react';
import { FileReferenceTag } from './FileReferenceTag';

interface MessageInputWithRichTextProps {
  value: string;
  onChange: (value: string) => void;
  onKeyPress: (e: React.KeyboardEvent) => void;
  attachedFiles: File[];
  fileReferences: Map<string, File>;
  disabled?: boolean;
}

export const MessageInputWithRichText: React.FC<MessageInputWithRichTextProps> = ({
  value,
  onChange,
  onKeyPress,
  fileReferences,
  disabled = false
}) => {
  const editableRef = useRef<HTMLDivElement>(null);
  const [isComposing, setIsComposing] = useState(false);

  // テキストとファイル参照を含むリッチコンテンツをレンダリング
  const renderContent = () => {
    if (!value || fileReferences.size === 0) {
      return <span className="text-text-muted">メッセージを入力...</span>;
    }

    const parts: (string | JSX.Element)[] = [];
    let lastIndex = 0;
    
    // ファイル参照パターンを検索
    const pattern = /\[([^\]]+)\]/g;
    let match;
    
    while ((match = pattern.exec(value)) !== null) {
      // マッチ前のテキスト
      if (match.index > lastIndex) {
        parts.push(value.substring(lastIndex, match.index));
      }
      
      // ファイル参照
      const fileName = match[1];
      const file = fileReferences.get(fileName);
      if (file) {
        parts.push(
          <FileReferenceTag
            key={`${fileName}-${match.index}`}
            fileName={fileName}
            fileType={file.type}
          />
        );
      } else {
        parts.push(match[0]); // ファイルが見つからない場合は元のテキスト
      }
      
      lastIndex = match.index + match[0].length;
    }
    
    // 残りのテキスト
    if (lastIndex < value.length) {
      parts.push(value.substring(lastIndex));
    }
    
    return parts;
  };

  // contentEditableの内容をプレーンテキストに変換
  const handleInput = () => {
    if (editableRef.current && !isComposing) {
      const text = editableRef.current.innerText || '';
      onChange(text);
    }
  };

  // キーボードイベントの処理
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      onKeyPress(e);
    }
  };

  // 外部からの値の変更を反映
  useEffect(() => {
    if (editableRef.current && !isComposing) {
      const currentText = editableRef.current.innerText || '';
      if (currentText !== value) {
        editableRef.current.innerHTML = '';
        const content = renderContent();
        if (React.isValidElement(content)) {
          editableRef.current.appendChild(document.createTextNode(value));
        } else if (Array.isArray(content)) {
          // リッチコンテンツは表示用で、実際の編集はプレーンテキスト
          editableRef.current.appendChild(document.createTextNode(value));
        }
      }
    }
  }, [value, isComposing, renderContent]);

  return (
    <div className="relative">
      <div
        ref={editableRef}
        contentEditable={!disabled}
        onInput={handleInput}
        onKeyDown={handleKeyDown}
        onCompositionStart={() => setIsComposing(true)}
        onCompositionEnd={() => setIsComposing(false)}
        className="w-full min-h-[44px] max-h-[200px] p-3 pr-12 bg-bg-secondary rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-blue/20 transition-all scrollbar-thin overflow-y-auto whitespace-pre-wrap"
        suppressContentEditableWarning
      />
      {value.length === 0 && (
        <div className="absolute top-3 left-3 pointer-events-none text-text-muted">
          メッセージを入力...
        </div>
      )}
      {/* リッチプレビュー */}
      <div className="absolute inset-0 pointer-events-none p-3 pr-12">
        <div className="whitespace-pre-wrap">{renderContent()}</div>
      </div>
    </div>
  );
};