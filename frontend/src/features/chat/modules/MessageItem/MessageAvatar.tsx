import React from 'react';
import { User, Bot } from 'lucide-react';
import { motion } from 'framer-motion';

interface MessageAvatarProps {
  role: 'user' | 'assistant';
}

export const MessageAvatar: React.FC<MessageAvatarProps> = ({ role }) => {
  const isUser = role === 'user';
  
  return (
    <motion.div 
      whileHover={{ scale: 1.1 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className={`
        w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 border transition-all duration-200
        ${isUser ? 'bg-primary-blue/10 border-primary-blue/20 hover:border-primary-blue/40' : 'bg-primary-green/10 border-primary-green/20 hover:border-primary-green/40'}
      `}
    >
      {isUser ? (
        <User className="w-5 h-5 text-primary-blue" />
      ) : (
        <Bot className="w-5 h-5 text-primary-green" />
      )}
    </motion.div>
  );
};