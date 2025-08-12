import React from 'react';
import { 
  Paperclip, 
  Globe, 
  Image, 
  Database, 
  ListTodo 
} from 'lucide-react';
import { motion } from 'framer-motion';

export interface ActionMenuItem {
  icon: React.ElementType;
  label: string;
  action: string;
}

interface ActionMenuProps {
  onAction: (action: string) => void;
  activeModes?: string[];
}

export const actionMenuItems: ActionMenuItem[] = [
  { icon: Paperclip, label: 'ファイル添付', action: 'attach' },
  { icon: Globe, label: 'Webクロール', action: 'webcrawl' },
  { icon: Image, label: '画像生成', action: 'image' },
  { icon: Database, label: 'RAGモード', action: 'rag' },
  { icon: ListTodo, label: 'タスク選択', action: 'task' },
];

export const ActionMenu: React.FC<ActionMenuProps> = ({ onAction, activeModes = [] }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95, y: 10 }}
      transition={{ duration: 0.15 }}
      className="absolute bottom-12 right-0 bg-white rounded-lg shadow-lg border border-border py-2 min-w-[180px] z-50"
    >
      {actionMenuItems.map((item, index) => {
        const Icon = item.icon;
        return (
          <motion.button
            key={item.action}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onAction(item.action)}
            className={`w-full flex items-center gap-3 px-4 py-2.5 hover:bg-bg-hover transition-colors text-left ${
              activeModes.includes(item.action) ? 'bg-primary-blue/10' : ''
            }`}
          >
            <Icon className={`w-4 h-4 ${
              activeModes.includes(item.action) ? 'text-primary-blue' : 'text-text-secondary'
            }`} />
            <span className={`text-sm ${
              activeModes.includes(item.action) ? 'text-primary-blue font-medium' : 'text-text-primary'
            }`}>{item.label}</span>
            {activeModes.includes(item.action) && (
              <div className="ml-auto">
                <div className="w-2 h-2 bg-primary-blue rounded-full animate-pulse" />
              </div>
            )}
          </motion.button>
        );
      })}
    </motion.div>
  );
};