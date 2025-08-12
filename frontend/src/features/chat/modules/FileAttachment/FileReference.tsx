import React from 'react';
import { FileText } from 'lucide-react';

interface FileReferenceProps {
  fileName: string;
}

export const FileReference: React.FC<FileReferenceProps> = ({ fileName }) => {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-blue/10 text-primary-blue rounded-md text-sm">
      <FileText className="w-3 h-3" />
      <span>{fileName}</span>
    </span>
  );
};