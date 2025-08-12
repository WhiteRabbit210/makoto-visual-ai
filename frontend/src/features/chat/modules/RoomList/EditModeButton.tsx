import React from 'react';
import { motion } from 'framer-motion';

interface EditModeButtonProps {
  isEditMode: boolean;
  onClick: () => void;
}

export const EditModeButton: React.FC<EditModeButtonProps> = ({ isEditMode, onClick }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`
        p-2.5 rounded-lg transition-all shadow-sm
        ${isEditMode 
          ? 'bg-status-error text-white' 
          : 'bg-bg-secondary text-text-secondary hover:bg-bg-hover hover:text-text-primary'
        }
      `}
      title={isEditMode ? '編集モードを終了' : '複数選択モード'}
    >
      <div className="relative w-5 h-5">
        {/* ゴミ箱の蓋 */}
        <motion.div
          animate={{ 
            rotate: isEditMode ? -30 : 0,
            x: isEditMode ? -3 : 0,
            y: isEditMode ? -3 : 0
          }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          style={{ transformOrigin: 'left center' }}
          className="absolute inset-x-0 top-0"
        >
          <svg
            width="20"
            height="6"
            viewBox="0 0 20 6"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="w-5"
          >
            <path
              d="M1 3C1 1.89543 1.89543 1 3 1H17C18.1046 1 19 1.89543 19 3V3C19 4.10457 18.1046 5 17 5H3C1.89543 5 1 4.10457 1 3V3Z"
              fill="currentColor"
            />
            <rect x="8" y="0" width="4" height="2" fill="currentColor" />
          </svg>
        </motion.div>
        
        {/* ゴミ箱の本体 */}
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="w-5 h-5"
        >
          <path
            d="M3 6H17V17C17 18.1046 16.1046 19 15 19H5C3.89543 19 3 18.1046 3 17V6Z"
            fill="currentColor"
          />
          <rect x="7" y="9" width="2" height="7" rx="1" fill={isEditMode ? 'white' : 'currentColor'} opacity="0.3" />
          <rect x="11" y="9" width="2" height="7" rx="1" fill={isEditMode ? 'white' : 'currentColor'} opacity="0.3" />
        </svg>
      </div>
    </motion.button>
  );
};