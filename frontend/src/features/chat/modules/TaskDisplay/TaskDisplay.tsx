import React, { useState } from 'react';
import { ChevronDown, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TaskDisplayProps {
  taskType: string;
  taskTemplate: string;
  taskDetails: string;
  onClose?: () => void;
}

export const TaskDisplay: React.FC<TaskDisplayProps> = ({ 
  taskTemplate, 
  taskDetails,
  onClose 
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className="bg-bg-secondary rounded-lg p-4 mb-4">
      {/* ヘッダー */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-base font-medium text-text-primary">タスク設定</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 hover:bg-bg-hover rounded transition-colors"
          >
            <ChevronDown 
              className={`w-4 h-4 text-text-secondary transition-transform ${
                isExpanded ? '' : '-rotate-90'
              }`}
            />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-1 hover:bg-bg-hover rounded transition-colors"
            >
              <X className="w-4 h-4 text-text-secondary" />
            </button>
          )}
        </div>
      </div>

      {/* 説明文 */}
      <div className="text-sm text-text-secondary mb-3">
        <p>AIにあらかじめ覚えておてほしい事やルールを設定できます。</p>
        <p>タスクテンプレート設定後に編集を加えても、元データには影響はありません。</p>
      </div>

      {/* 免責事項 */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border pt-3">
              <h4 className="text-sm font-medium text-text-primary mb-2">免責事項</h4>
              <div className="bg-bg-primary rounded-lg p-3">
                {/* タスクテンプレート */}
                <div className="mb-3">
                  <div className="flex items-center justify-between p-3 bg-bg-secondary rounded-lg">
                    <span className="text-sm text-text-primary">{taskTemplate}</span>
                    <ChevronDown className="w-4 h-4 text-text-muted" />
                  </div>
                </div>

                {/* タスク詳細 */}
                {taskDetails && (
                  <div className="text-sm text-text-secondary space-y-2">
                    {taskDetails.split('\n').map((line, index) => (
                      <p key={index}>{line}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};