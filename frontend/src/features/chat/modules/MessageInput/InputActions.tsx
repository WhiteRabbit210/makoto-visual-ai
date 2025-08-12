import React, { useState, useEffect, useRef } from 'react';
import { AnimatePresence } from 'framer-motion';
import { ActionMenu, ActionMenuButton } from './ActionMenu';
import { SendButton } from './SendButton';

interface InputActionsProps {
  onSend: () => void;
  isDisabled: boolean;
  isLoading: boolean;
  onAttachFile?: () => void;
  canAttachMore?: boolean;
  onTaskSelect?: () => void;
  currentTask?: { type: string; template: string; details: string } | null;
  onModeToggle?: (mode: string) => void;
  activeModes?: Array<{ id: string; label: string }>;
}

export const InputActions: React.FC<InputActionsProps> = ({ 
  onSend, 
  isDisabled, 
  onAttachFile,
  canAttachMore = true,
  onTaskSelect,
  onModeToggle,
  activeModes = []
}) => {
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleMenuAction = (action: string) => {
    console.log(`Action: ${action}`);
    if (action === 'attach' && onAttachFile && canAttachMore) {
      onAttachFile();
    } else if (action === 'task' && onTaskSelect) {
      onTaskSelect();
    } else if ((action === 'webcrawl' || action === 'image' || action === 'rag') && onModeToggle) {
      onModeToggle(action);
    }
    setShowMenu(false);
    // ここで各アクションの処理を実装
  };

  // メニュー外クリックで閉じる
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false);
      }
    };

    if (showMenu) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showMenu]);

  return (
    <>
      {/* アクションメニュー */}
      <div className="relative" ref={menuRef}>
        <ActionMenuButton 
          isOpen={showMenu} 
          onClick={() => setShowMenu(!showMenu)} 
        />
        
        <AnimatePresence>
          {showMenu && (
            <ActionMenu 
              onAction={handleMenuAction} 
              activeModes={activeModes.map(m => m.id)}
            />
          )}
        </AnimatePresence>
      </div>

      {/* 送信ボタン */}
      <SendButton 
        onClick={onSend}
        isDisabled={isDisabled}
      />
    </>
  );
};