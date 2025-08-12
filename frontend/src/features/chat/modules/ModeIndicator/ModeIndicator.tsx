import React from 'react';
import { Globe, Image, Database } from 'lucide-react';
import { motion } from 'framer-motion';

interface ModeIndicatorProps {
  mode: 'webcrawl' | 'image' | 'rag';
}

const modeConfigs = {
  webcrawl: {
    icon: Globe,
    label: 'Web',
    color: 'text-green-600',
    bgColor: 'bg-green-500',
    pulseColor: 'bg-green-400',
  },
  image: {
    icon: Image,
    label: '画像',
    color: 'text-purple-600',
    bgColor: 'bg-purple-500',
    pulseColor: 'bg-purple-400',
  },
  rag: {
    icon: Database,
    label: 'RAG',
    color: 'text-blue-600',
    bgColor: 'bg-blue-500',
    pulseColor: 'bg-blue-400',
  },
};

export const ModeIndicator: React.FC<ModeIndicatorProps> = ({ mode }) => {
  const config = modeConfigs[mode];
  const Icon = config.icon;

  return (
    <div className="fixed bottom-24 right-6 z-40">
      <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3, type: "spring" }}
        className="relative"
      >
        {/* パルスアニメーション */}
        <div className={`absolute inset-0 ${config.pulseColor} rounded-full animate-ping opacity-20`} />
        
        {/* メインインジケーター */}
        <div className={`
          relative flex items-center gap-2 px-4 py-2.5 
          ${config.bgColor} text-white rounded-full shadow-lg
          backdrop-blur-sm border border-white/20
        `}>
          <Icon className="w-5 h-5" />
          <span className="text-sm font-medium">{config.label}モード</span>
        </div>

        {/* 光るドット */}
        <div className="absolute -top-1 -right-1">
          <span className="relative flex h-3 w-3">
            <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${config.bgColor} opacity-75`}></span>
            <span className={`relative inline-flex rounded-full h-3 w-3 ${config.bgColor}`}></span>
          </span>
        </div>
      </motion.div>
    </div>
  );
};