import React from 'react';
import { Plus } from 'lucide-react';
import { motion } from 'framer-motion';

interface TopBannerProps {
  title: string;
  subtitle: string;
  onAction?: () => void;
  actionLabel?: string;
}

export const TopBanner: React.FC<TopBannerProps> = ({
  title,
  subtitle,
  onAction,
  actionLabel
}) => {
  return (
    <div className="bg-white rounded-lg border border-border p-6 mb-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text-primary mb-1">{title}</h1>
          <p className="text-sm text-text-secondary">{subtitle}</p>
        </div>
        {onAction && (
          <motion.button
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            onClick={onAction}
            className="flex items-center gap-2 px-4 py-2 bg-primary-blue hover:bg-primary-blue/90 
              text-white rounded-lg transition-all duration-200 hover:shadow-lg"
          >
            <Plus className="w-4 h-4" />
            <span className="text-sm font-medium">{actionLabel}</span>
          </motion.button>
        )}
      </div>
    </div>
  );
};