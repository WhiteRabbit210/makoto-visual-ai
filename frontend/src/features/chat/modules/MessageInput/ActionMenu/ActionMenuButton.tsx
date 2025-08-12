import React from 'react';
import { Plus } from 'lucide-react';
import { motion } from 'framer-motion';

interface ActionMenuButtonProps {
  isOpen: boolean;
  onClick: () => void;
}

export const ActionMenuButton: React.FC<ActionMenuButtonProps> = ({ isOpen, onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className="p-2.5 text-text-secondary hover:text-text-primary hover:bg-bg-hover rounded-lg transition-all"
    >
      <motion.div
        animate={{ rotate: isOpen ? 225 : 0 }}
        transition={{ 
          duration: 0.5, 
          ease: [0.68, -0.55, 0.265, 1.55],
          type: "spring",
          stiffness: 260,
          damping: 20
        }}
      >
        <Plus className="w-5 h-5" />
      </motion.div>
    </motion.button>
  );
};