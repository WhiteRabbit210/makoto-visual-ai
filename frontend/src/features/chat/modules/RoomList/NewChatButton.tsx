import React from 'react';
import { Plus } from 'lucide-react';
import { motion } from 'framer-motion';

interface NewChatButtonProps {
  onClick: () => void;
}

export const NewChatButton: React.FC<NewChatButtonProps> = ({ onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className="flex-1 flex items-center justify-center gap-2 bg-primary-blue text-white px-4 py-2.5 rounded-lg hover:bg-blue-600 transition-colors shadow-sm"
    >
      <motion.div
        whileHover={{ rotate: 720 }}
        transition={{ duration: 0.5, ease: "easeInOut" }}
      >
        <Plus className="w-5 h-5" />
      </motion.div>
      <span className="font-medium">新規チャット</span>
    </motion.button>
  );
};