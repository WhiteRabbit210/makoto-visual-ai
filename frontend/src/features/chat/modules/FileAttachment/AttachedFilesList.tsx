import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { AttachedFile } from './AttachedFile';

interface AttachedFilesListProps {
  files: File[];
  onRemove: (index: number) => void;
  onFileClick: (file: File) => void;
}

export const AttachedFilesList: React.FC<AttachedFilesListProps> = ({ 
  files, 
  onRemove, 
  onFileClick 
}) => {
  if (files.length === 0) return null;

  return (
    <div className="flex gap-2 p-2 border-t border-border">
      <AnimatePresence>
        {files.map((file, index) => (
          <AttachedFile
            key={`${file.name}-${index}`}
            file={file}
            onRemove={() => onRemove(index)}
            onClick={() => onFileClick(file)}
          />
        ))}
      </AnimatePresence>
    </div>
  );
};