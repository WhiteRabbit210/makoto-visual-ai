import React from 'react';
import { X, FileText, Image, File } from 'lucide-react';
import { motion } from 'framer-motion';

interface AttachedFileProps {
  file: File;
  onRemove: () => void;
  onClick: () => void;
}

export const AttachedFile: React.FC<AttachedFileProps> = ({ file, onRemove, onClick }) => {
  const getFileIcon = () => {
    const type = file.type;
    if (type.startsWith('image/')) return Image;
    if (type.includes('pdf') || type.includes('document')) return FileText;
    return File;
  };

  const Icon = getFileIcon();
  const fileName = file.name.length > 20 
    ? file.name.substring(0, 17) + '...' 
    : file.name;

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      className="relative group"
    >
      <button
        onClick={onClick}
        className="flex items-center gap-2 px-3 py-2 bg-bg-secondary rounded-lg border border-border hover:border-primary-blue/30 transition-all"
      >
        <Icon className="w-4 h-4 text-text-secondary" />
        <span className="text-sm text-text-primary">{fileName}</span>
      </button>
      
      <button
        onClick={(e) => {
          e.stopPropagation();
          onRemove();
        }}
        className="absolute -top-2 -right-2 w-5 h-5 bg-status-error text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <X className="w-3 h-3" />
      </button>
    </motion.div>
  );
};