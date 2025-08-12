import React from 'react';
import { motion } from 'framer-motion';
import { Bot, Brain, Sparkles, Search, Image, Globe } from 'lucide-react';

interface AgentThinkingProps {
  isVisible: boolean;
  status?: 'analyzing' | 'searching' | 'crawling' | 'generating';
  details?: string;
}

export const AgentThinking: React.FC<AgentThinkingProps> = ({ isVisible, status = 'analyzing', details }) => {
  if (!isVisible) return null;

  // ステータスに基づくアイコン選択
  const getIcon = () => {
    switch (status) {
      case 'searching':
        return <Search className="w-10 h-10 text-blue-500" />;
      case 'crawling':
        return <Globe className="w-10 h-10 text-green-500" />;
      case 'generating':
        return <Image className="w-10 h-10 text-purple-500" />;
      default:
        return <Bot className="w-10 h-10 text-primary" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="flex items-center justify-center py-8"
    >
      <div className="bg-surface-hover border border-primary/20 rounded-lg p-6 max-w-lg">
        <div className="flex items-center gap-4">
          {/* アニメーションするアイコン */}
          <div className="relative">
            {getIcon()}
            
            {/* 思考中のアニメーション */}
            <motion.div
              className="absolute -top-2 -right-2"
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.2, 1]
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "linear"
              }}
            >
              <Brain className="w-4 h-4 text-primary/70" />
            </motion.div>
            
            {/* キラキラエフェクト */}
            <motion.div
              className="absolute -bottom-1 -left-1"
              animate={{ 
                opacity: [0, 1, 0],
                scale: [0.8, 1.2, 0.8]
              }}
              transition={{ 
                duration: 1.5,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <Sparkles className="w-3 h-3 text-yellow-500" />
            </motion.div>
          </div>
          
          {/* テキスト */}
          <div className="flex-1">
            <h3 className="text-sm font-medium text-text-primary mb-1">
              {
                status === 'analyzing' ? 'エージェントが分析中...' :
                status === 'searching' ? 'Webから情報を検索中...' :
                status === 'crawling' ? 'ページを収集中...' :
                status === 'generating' ? '画像を生成中...' :
                '処理中...'
              }
            </h3>
            <p className="text-xs text-text-secondary">
              {
                status === 'analyzing' ? details || '最適な回答方法を検討しています' :
                status === 'searching' ? details || 'Googleで最新情報を検索しています' :
                status === 'crawling' ? details || '上位5サイトから情報を収集しています' :
                status === 'generating' ? details || 'AIで画像を生成しています' :
                'しばらくお待ちください'
              }
            </p>
            
            {/* 詳細情報がある場合に表示 */}
            {details && (
              <div className="mt-2 p-2 bg-surface rounded text-xs text-text-muted">
                🤖 {details}
              </div>
            )}
            
            {/* プログレスバー */}
            <div className="mt-2 h-1 bg-surface rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-indigo-600"
                animate={{ 
                  x: ['-100%', '100%']
                }}
                transition={{ 
                  duration: 1.5,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                style={{ width: '50%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};