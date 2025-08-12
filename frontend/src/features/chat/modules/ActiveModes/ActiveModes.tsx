import React from 'react';
import { Globe, Image, Database, X, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface ActiveMode {
  id: string;
  name: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
}

interface ActiveModesProps {
  activeModes: ActiveMode[];
  onRemoveMode: (modeId: string) => void;
}

const modeConfigs = {
  webcrawl: {
    name: 'Webクロール',
    icon: Globe,
    color: 'text-green-600',
    bgColor: 'bg-green-50 border-green-200',
  },
  image: {
    name: '画像生成',
    icon: Image,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50 border-purple-200',
  },
  rag: {
    name: 'RAGモード',
    icon: Database,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50 border-blue-200',
  },
  agent: {
    name: 'エージェント',
    icon: Bot,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50 border-orange-200',
  },
};

export const ActiveModes: React.FC<ActiveModesProps> = ({ activeModes, onRemoveMode }) => {
  // エージェントモードは表示しない
  const displayModes = activeModes.filter(mode => mode.id !== 'agent');
  if (displayModes.length === 0) return null;

  return (
    <div className="px-4 py-3 border-b border-border bg-gradient-to-r from-bg-secondary/30 to-bg-secondary/10">
      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-xs text-text-muted font-medium">アクティブモード:</span>
        <AnimatePresence>
          {displayModes.map((mode) => {
            const config = modeConfigs[mode.id as keyof typeof modeConfigs];
            if (!config) return null;
            
            const Icon = config.icon;
            
            return (
              <motion.div
                key={mode.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
                className={`
                  inline-flex items-center gap-2 px-3 py-1.5 rounded-full border
                  ${config.bgColor} ${config.color}
                  group transition-all hover:shadow-md
                `}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{config.name}</span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveMode(mode.id);
                  }}
                  className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity hover:scale-110"
                >
                  <X className="w-3 h-3" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};