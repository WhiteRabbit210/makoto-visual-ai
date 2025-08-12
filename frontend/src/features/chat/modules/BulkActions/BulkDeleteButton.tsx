import React from 'react';
import { Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface BulkDeleteButtonProps {
  selectedCount: number;
  onDelete: () => void;
}

export const BulkDeleteButton: React.FC<BulkDeleteButtonProps> = ({ 
  selectedCount, 
  onDelete 
}) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onDelete}
      className="w-full flex items-center justify-center gap-2 bg-status-error text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors shadow-sm"
    >
      <Trash2 className="w-4 h-4" />
      <span className="text-sm font-medium">
        {selectedCount}件のチャットを削除
      </span>
    </motion.button>
  );
};