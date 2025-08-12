import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export const ImageGeneratingIndicator: React.FC = () => {
  return (
    <div className="flex items-center gap-3 p-4 bg-secondary rounded-lg border border-border">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      >
        <Loader2 className="w-5 h-5 text-primary" />
      </motion.div>
      <span className="text-sm text-text-muted">画像を生成中...</span>
      <div className="flex gap-1 ml-2">
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className="w-1.5 h-1.5 bg-primary/50 rounded-full"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 1, 0.3],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.2,
            }}
          />
        ))}
      </div>
    </div>
  );
};