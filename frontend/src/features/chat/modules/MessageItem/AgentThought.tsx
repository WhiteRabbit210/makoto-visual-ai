import React from 'react';
import { motion } from 'framer-motion';

interface AgentThoughtProps {
  content: string;
  timestamp: string;
  status?: 'thinking' | 'analyzing' | 'searching' | 'crawling' | 'generating' | 'complete';
}

export const AgentThought: React.FC<AgentThoughtProps> = ({ 
  content, 
  timestamp,
  status = 'thinking' 
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'thinking':
        return '🤔';
      case 'analyzing':
        return '🔍';
      case 'searching':
        return '🌐';
      case 'crawling':
        return '🕸️';
      case 'generating':
        return '🎨';
      case 'complete':
        return '✅';
      default:
        return '💭';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className="flex justify-start mb-4"
    >
      <div className="flex max-w-[70%] items-start gap-3">
        {/* エージェントアバター */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
          <span className="text-sm">{getStatusIcon()}</span>
        </div>
        
        {/* 思考バブル */}
        <div className="flex flex-col">
          <div className="bg-gray-100/50 dark:bg-gray-800/50 rounded-2xl px-4 py-3 backdrop-blur-sm">
            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
              {content}
            </p>
          </div>
          
          {/* タイムスタンプ */}
          <div className="mt-1 px-2">
            <span className="text-xs text-gray-400 dark:text-gray-500">
              {timestamp}
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
};