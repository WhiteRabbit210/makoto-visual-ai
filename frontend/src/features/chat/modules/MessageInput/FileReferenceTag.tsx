import React from 'react';
import { FileText, Image, File, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface FileReferenceTagProps {
  fileName: string;
  fileType: string;
  onRemove?: () => void;
}

export const FileReferenceTag: React.FC<FileReferenceTagProps> = ({ 
  fileName, 
  fileType,
  onRemove 
}) => {
  const getFileIcon = () => {
    if (fileType.startsWith('image/')) return Image;
    if (fileType.includes('pdf') || fileType.includes('document')) return FileText;
    return File;
  };

  const Icon = getFileIcon();
  const displayName = fileName.length > 15 
    ? fileName.substring(0, 12) + '...' + fileName.substring(fileName.lastIndexOf('.'))
    : fileName;

  return (
    <motion.span
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="inline-flex items-center gap-1.5 px-2.5 py-1 mx-1 bg-gradient-to-r from-primary-blue/10 to-primary-blue/5 border border-primary-blue/20 rounded-lg group hover:border-primary-blue/40 transition-all"
    >
      <Icon className="w-3.5 h-3.5 text-primary-blue" />
      <span className="text-sm font-medium text-primary-blue">{displayName}</span>
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-1 opacity-0 group-hover:opacity-100 transition-opacity"
        >
          <X className="w-3 h-3 text-primary-blue/60 hover:text-primary-blue" />
        </button>
      )}
    </motion.span>
  );
};