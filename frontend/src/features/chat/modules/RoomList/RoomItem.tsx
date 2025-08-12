import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Trash2, Check } from 'lucide-react';
import { motion } from 'framer-motion';
import { RoomItemSkeleton } from './RoomItemSkeleton';

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

interface RoomItemProps {
  chat: Chat;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
  index?: number;
  isEditMode?: boolean;
  isSelected?: boolean;
  onToggleSelect?: () => void;
}

export const RoomItem: React.FC<RoomItemProps> = ({
  chat,
  isActive,
  onClick,
  onDelete,
  isEditMode = false,
  isSelected = false,
  onToggleSelect,
}) => {
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

  const handleClick = () => {
    if (isEditMode && onToggleSelect) {
      onToggleSelect();
    } else {
      onClick();
    }
  };

  return (
    <div ref={itemRef} className="relative">
      {/* スケルトン - フェードアウト */}
      <div
        className={`absolute inset-0 transition-opacity duration-300 ${
          isRendered ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
      >
        <RoomItemSkeleton />
      </div>

      {/* 実際のアイテム - フェードイン */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isRendered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        whileHover={{ x: isEditMode || !isRendered ? 0 : 4 }}
        className={`
          group relative flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-all
          ${isActive && !isEditMode ? 'bg-primary-blue/10 border border-primary-blue/20' : 'hover:bg-bg-hover'}
          ${isSelected ? 'bg-primary-blue/5 border border-primary-blue/30' : ''}
          ${!isRendered ? 'pointer-events-none' : ''}
        `}
        onClick={handleClick}
      >
      {isEditMode ? (
        <div className="relative w-5 h-5 mt-0.5 flex-shrink-0">
          <div 
            className={`
              w-5 h-5 rounded border-2 transition-all
              ${isSelected 
                ? 'bg-primary-blue border-primary-blue' 
                : 'bg-bg-primary border-border hover:border-primary-blue/50'
              }
            `}
          >
            {isSelected && (
              <Check className="w-3 h-3 text-white absolute top-0.5 left-0.5" />
            )}
          </div>
        </div>
      ) : (
        <MessageSquare className={`w-5 h-5 mt-0.5 flex-shrink-0 ${isActive ? 'text-primary-blue' : 'text-text-secondary'}`} />
      )}
      
      <div className="flex-1 min-w-0">
        <h3 className={`font-medium truncate ${isActive && !isEditMode ? 'text-primary-blue' : 'text-text-primary'}`}>
          {chat.title}
        </h3>
        <p className="text-sm text-text-muted truncate mt-0.5">{chat.lastMessage}</p>
        <div className="flex items-center gap-2 mt-1">
          <p className="text-xs text-text-muted">{chat.timestamp}</p>
          <span className="text-xs text-text-muted/60">•</span>
          <p className="text-xs text-text-muted/60 font-mono truncate" title={chat.id}>
            {chat.id.slice(0, 8)}...
          </p>
        </div>
      </div>
      
      {!isEditMode && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-bg-secondary rounded"
        >
          <Trash2 className="w-4 h-4 text-text-muted hover:text-status-error transition-colors" />
        </button>
      )}
      </motion.div>
    </div>
  );
};