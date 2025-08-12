import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NewChatButton } from '../RoomList/NewChatButton';
import { EditModeButton } from '../RoomList/EditModeButton';
import { BulkDeleteButton } from '../BulkActions';

interface ChatHeaderProps {
  isEditMode: boolean;
  selectedCount: number;
  onNewChat: () => void;
  onToggleEditMode: () => void;
  onBulkDelete: () => void;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  isEditMode,
  selectedCount,
  onNewChat,
  onToggleEditMode,
  onBulkDelete,
}) => {
  return (
    <div className="p-4 border-b border-border">
      <div className="flex gap-2">
        <NewChatButton onClick={onNewChat} />
        <EditModeButton isEditMode={isEditMode} onClick={onToggleEditMode} />
      </div>
      
      <AnimatePresence>
        {isEditMode && selectedCount > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-3"
          >
            <BulkDeleteButton 
              selectedCount={selectedCount}
              onDelete={onBulkDelete}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};