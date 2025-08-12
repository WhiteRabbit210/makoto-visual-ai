import React, { useState } from 'react';
import { Copy, Check, ThumbsUp, ThumbsDown } from 'lucide-react';
import { motion } from 'framer-motion';

interface MessageActionsProps {
  messageId?: string;
  content: string;
  isUser: boolean;
  feedback: 'good' | 'bad' | null;
  onFeedback: (type: 'good' | 'bad') => void;
}

export const MessageActions: React.FC<MessageActionsProps> = ({ 
  content, 
  isUser, 
  feedback, 
  onFeedback 
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <div className={`
      absolute opacity-0 group-hover:opacity-100 transition-opacity duration-200
      flex gap-1 bottom-0
      ${isUser ? '-left-10' : '-right-28'}
    `}>
      {/* Copy Button */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={handleCopy}
        className="p-1.5 bg-white border border-border rounded-lg shadow-sm hover:bg-bg-hover"
      >
        {isCopied ? (
          <Check className="w-3.5 h-3.5 text-primary-green" />
        ) : (
          <Copy className="w-3.5 h-3.5 text-text-secondary" />
        )}
      </motion.button>
      
      {/* Good Button - AIメッセージのみ */}
      {!isUser && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onFeedback('good')}
          className={`p-1.5 bg-white border rounded-lg shadow-sm transition-all duration-200
            ${feedback === 'good' 
              ? 'border-primary-green bg-primary-green/10' 
              : 'border-border hover:bg-bg-hover'
            }
          `}
        >
          <ThumbsUp className={`w-3.5 h-3.5 ${
            feedback === 'good' ? 'text-primary-green' : 'text-text-secondary'
          }`} />
        </motion.button>
      )}
      
      {/* Bad Button - AIメッセージのみ */}
      {!isUser && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onFeedback('bad')}
          className={`p-1.5 bg-white border rounded-lg shadow-sm transition-all duration-200
            ${feedback === 'bad' 
              ? 'border-status-error bg-status-error/10' 
              : 'border-border hover:bg-bg-hover'
            }
          `}
        >
          <ThumbsDown className={`w-3.5 h-3.5 ${
            feedback === 'bad' ? 'text-status-error' : 'text-text-secondary'
          }`} />
        </motion.button>
      )}
    </div>
  );
};