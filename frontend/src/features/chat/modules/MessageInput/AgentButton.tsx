import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

interface AgentButtonProps {
  isActive: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export const AgentButton: React.FC<AgentButtonProps> = ({ isActive, onClick, disabled }) => {
  return (
    <div className="relative group">
      {/* ツールチップ */}
      <div className={`
        absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 
        bg-gray-900 text-white text-xs rounded-lg whitespace-nowrap
        pointer-events-none transition-all duration-200
        ${isActive ? 'opacity-0 group-hover:opacity-100' : 'opacity-0 group-hover:opacity-100'}
      `}>
        {isActive ? 'エージェントが最適な回答方法を選択します' : 'エージェント機能を有効化'}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 
          border-4 border-transparent border-t-gray-900" />
      </div>
      
      <motion.button
      onClick={onClick}
      disabled={disabled}
      className={`
        relative w-10 h-10 rounded-full flex items-center justify-center
        transition-all duration-300 group
        ${isActive 
          ? 'bg-gradient-to-br from-violet-500 via-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/40 border border-transparent' 
          : 'bg-surface text-text-secondary hover:text-primary border border-border hover:border-primary/30'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      whileHover={!disabled ? { scale: 1.1 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
    >
      {/* AIロボットアイコン */}
      <motion.div
        animate={isActive ? {
          rotate: [0, -10, 10, -10, 10, 0],
        } : {}}
        transition={{
          duration: 0.5,
          repeat: isActive ? Infinity : 0,
          repeatDelay: 2
        }}
      >
        <Bot 
          className={`w-5 h-5 ${isActive ? 'drop-shadow-lg' : 'group-hover:text-primary'} transition-all duration-300`} 
          strokeWidth={2} 
        />
      </motion.div>
      
      {/* アクティブ時のカラフルな光のエフェクト */}
      {isActive && (
        <>
          {/* グラデーショングロウ */}
          <motion.div
            className="absolute inset-0 rounded-full pointer-events-none"
            animate={{ 
              opacity: [0.2, 0.5, 0.2],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
            style={{ 
              background: 'radial-gradient(circle at center, rgba(147, 51, 234, 0.4) 0%, transparent 60%)',
              filter: 'blur(8px)'
            }}
          />
          
          {/* パーティクルエフェクト */}
          {/* 上部のパーティクル群 */}
          <motion.div
            className="absolute -top-1 -right-1 w-1.5 h-1.5 bg-pink-400 rounded-full shadow-lg shadow-pink-400/50"
            animate={{
              x: [0, 5, -2, 0],
              y: [0, -12, -15, -18],
              opacity: [0, 1, 1, 0],
              scale: [0, 1.2, 0.8, 0]
            }}
            transition={{
              duration: 2.5,
              repeat: Infinity,
              delay: 0,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute top-0 left-1/2 w-1 h-1 bg-yellow-400 rounded-full shadow-lg shadow-yellow-400/50"
            animate={{
              x: [-2, -7, -5, -10],
              y: [0, -10, -14, -18],
              opacity: [0, 1, 0.8, 0],
              scale: [0, 1, 0.6, 0]
            }}
            transition={{
              duration: 2.2,
              repeat: Infinity,
              delay: 0.3,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute -top-0.5 -left-0.5 w-1.5 h-1.5 bg-violet-400 rounded-full shadow-lg shadow-violet-400/50"
            animate={{
              x: [-2, -6, -4, -8],
              y: [0, -11, -13, -16],
              opacity: [0, 1, 0.9, 0],
              scale: [0, 1.1, 0.7, 0]
            }}
            transition={{
              duration: 2.3,
              repeat: Infinity,
              delay: 0.6,
              ease: "easeOut"
            }}
          />
          
          {/* 下部のパーティクル群 */}
          <motion.div
            className="absolute -bottom-1 -left-1 w-1.5 h-1.5 bg-cyan-400 rounded-full shadow-lg shadow-cyan-400/50"
            animate={{
              x: [-2, -7, -5, -9],
              y: [0, 10, 12, 15],
              opacity: [0, 1, 0.8, 0],
              scale: [0, 1.1, 0.7, 0]
            }}
            transition={{
              duration: 2.4,
              repeat: Infinity,
              delay: 0.9,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute bottom-0 right-1/3 w-1 h-1 bg-purple-400 rounded-full shadow-lg shadow-purple-400/50"
            animate={{
              x: [0, 6, 4, 8],
              y: [0, 9, 12, 15],
              opacity: [0, 1, 0.7, 0],
              scale: [0, 0.8, 0.5, 0]
            }}
            transition={{
              duration: 2.1,
              repeat: Infinity,
              delay: 1.2,
              ease: "easeOut"
            }}
          />
          
          {/* 中央から飛び散る小さなパーティクル */}
          <motion.div
            className="absolute top-1/2 left-1/2 w-0.5 h-0.5 bg-white rounded-full"
            animate={{
              x: [-0.5, -4, -6],
              y: [-0.5, -4, -6],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: 0.1,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute top-1/2 left-1/2 w-0.5 h-0.5 bg-white rounded-full"
            animate={{
              x: [0.5, 4, 6],
              y: [-0.5, -4, -6],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: 0.4,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute top-1/2 left-1/2 w-0.5 h-0.5 bg-white rounded-full"
            animate={{
              x: [0.5, 4, 6],
              y: [0.5, 4, 6],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: 0.7,
              ease: "easeOut"
            }}
          />
          <motion.div
            className="absolute top-1/2 left-1/2 w-0.5 h-0.5 bg-white rounded-full"
            animate={{
              x: [-0.5, -4, -6],
              y: [0.5, 4, 6],
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0]
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: 1.0,
              ease: "easeOut"
            }}
          />
        </>
      )}
      
      {/* 外側のリングアニメーション */}
      {isActive && (
        <motion.span
          className="absolute inset-0 rounded-full"
          initial={{ scale: 1, opacity: 0 }}
          animate={{ 
            scale: [1, 1.5, 1.5],
            opacity: [0, 0.6, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeOut"
          }}
          style={{
            background: 'linear-gradient(45deg, rgba(167, 139, 250, 0.5), rgba(236, 72, 153, 0.5))',
            border: '2px solid transparent',
            backgroundClip: 'padding-box'
          }}
        />
      )}
      </motion.button>
    </div>
  );
};