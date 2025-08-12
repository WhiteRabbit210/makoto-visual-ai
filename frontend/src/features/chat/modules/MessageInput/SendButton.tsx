import React from 'react';
import { Send } from 'lucide-react';
import { motion } from 'framer-motion';

interface SendButtonProps {
  onClick: () => void;
  isDisabled: boolean;
}

export const SendButton: React.FC<SendButtonProps> = ({ onClick, isDisabled }) => {
  return (
    <motion.button
      whileHover={{ scale: isDisabled ? 1 : 1.05 }}
      whileTap={{ scale: isDisabled ? 1 : 0.95 }}
      onClick={onClick}
      disabled={isDisabled}
      className={`
        p-2.5 rounded-lg transition-all shadow-sm
        ${isDisabled 
          ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
          : 'bg-primary-blue text-white hover:bg-blue-600'
        }
      `}
    >
      <Send className="w-5 h-5" />
    </motion.button>
  );
};