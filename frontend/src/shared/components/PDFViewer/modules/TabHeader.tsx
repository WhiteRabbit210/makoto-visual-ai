import React from 'react';
import { FileText } from 'lucide-react';

interface PDFSource {
  id: string;
  title: string;
  url: string;
  pages: number;
}

interface TabHeaderProps {
  sources: PDFSource[];
  activeTab: number;
  onTabChange: (index: number) => void;
}

export const TabHeader: React.FC<TabHeaderProps> = ({ sources, activeTab, onTabChange }) => {
  return (
    <div className="flex border-b border-gray-200">
      {sources.map((source, index) => (
        <button
          key={source.id}
          onClick={() => onTabChange(index)}
          className={`
            flex-1 px-3 py-2 text-sm font-medium transition-all duration-200
            ${activeTab === index 
              ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' 
              : 'hover:bg-gray-50 text-gray-600'
            }
          `}
        >
          <div className="flex items-center justify-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            <span className="truncate max-w-[100px]">{source.title}</span>
          </div>
        </button>
      ))}
    </div>
  );
};