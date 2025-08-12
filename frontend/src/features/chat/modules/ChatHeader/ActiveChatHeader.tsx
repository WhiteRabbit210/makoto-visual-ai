import React from 'react';
import { MessageSquare, Copy, Check } from 'lucide-react';
import { motion } from 'framer-motion';

interface ActiveChatHeaderProps {
  chatId: string | null;
  chatTitle?: string;
}

export const ActiveChatHeader: React.FC<ActiveChatHeaderProps> = ({ chatId, chatTitle }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopyId = () => {
    if (chatId) {
      navigator.clipboard.writeText(chatId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!chatId) {
    return (
      <div className="h-14 border-b border-border flex items-center px-4">
        <div className="flex items-center gap-3 text-text-muted">
          <MessageSquare className="w-5 h-5" />
          <span className="text-sm">新しいチャット</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="h-14 border-b border-border flex items-center justify-between px-4"
    >
      <div className="flex items-center gap-3 min-w-0">
        <MessageSquare className="w-5 h-5 text-primary-blue flex-shrink-0" />
        <div className="min-w-0">
          <h2 className="font-medium text-text-primary truncate">
            {chatTitle || '無題のチャット'}
          </h2>
          <div className="flex items-center gap-2">
            <p className="text-xs text-text-muted font-mono">
              ID: {chatId.slice(0, 8)}...{chatId.slice(-4)}
            </p>
            <button
              onClick={handleCopyId}
              className="p-1 hover:bg-bg-hover rounded transition-colors"
              title="IDをコピー"
            >
              {copied ? (
                <Check className="w-3 h-3 text-status-success" />
              ) : (
                <Copy className="w-3 h-3 text-text-muted" />
              )}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};