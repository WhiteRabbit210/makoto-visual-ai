import React, { useRef, useEffect, forwardRef } from 'react';

interface AutoResizeTextareaProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onKeyPress: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
  maxHeight?: number;
  minHeight?: number;
}

export const AutoResizeTextarea = forwardRef<HTMLTextAreaElement, AutoResizeTextareaProps>(
  ({ 
    value, 
    onChange, 
    onKeyPress, 
    placeholder = "メッセージを入力...", 
    disabled = false,
    className = "",
    maxHeight = 200,
    minHeight = 44
  }, ref) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const combinedRef = ref || textareaRef;
    const isComposingRef = useRef(false);

    // テキストエリアの高さを自動調整
    useEffect(() => {
      const textarea = typeof combinedRef === 'function' ? null : combinedRef.current;
      if (textarea) {
        // 一旦高さをリセット
        textarea.style.height = 'auto';
        // スクロール高さに合わせて調整
        const scrollHeight = textarea.scrollHeight;
        // 最大高さと最小高さの範囲内で調整
        textarea.style.height = Math.min(Math.max(scrollHeight, minHeight), maxHeight) + 'px';
      }
    }, [value, maxHeight, minHeight, combinedRef]);

    // 日本語入力中の判定
    const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (!isComposingRef.current) {
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
      <textarea
        ref={combinedRef}
        value={value}
        onChange={onChange}
        onKeyPress={handleKeyPress}
        onCompositionStart={handleCompositionStart}
        onCompositionEnd={handleCompositionEnd}
        placeholder={placeholder}
        disabled={disabled}
        className={`w-full p-3 pr-12 bg-bg-secondary border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue/30 transition-all scrollbar-thin overflow-y-auto ${className}`}
        style={{ minHeight: `${minHeight}px` }}
      />
    );
  }
);

AutoResizeTextarea.displayName = 'AutoResizeTextarea';