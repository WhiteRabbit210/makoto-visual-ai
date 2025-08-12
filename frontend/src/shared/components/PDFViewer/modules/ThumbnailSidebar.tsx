import React from 'react';
import { Document, Page } from 'react-pdf';

interface ThumbnailSidebarProps {
  sourceUrl: string;
  totalPages: number;
  currentPage: number;
  onPageChange: (pageNum: number) => void;
}

export const ThumbnailSidebar: React.FC<ThumbnailSidebarProps> = ({
  sourceUrl,
  totalPages,
  currentPage,
  onPageChange
}) => {
  return (
    <div 
      className="w-32 bg-white border-r border-gray-200 overflow-y-auto focus:outline-none"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'ArrowUp') {
          e.preventDefault();
          onPageChange(Math.max(1, currentPage - 1));
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          onPageChange(Math.min(totalPages, currentPage + 1));
        }
      }}
    >
      <div className="p-2 space-y-2">
        {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
          <button
            key={pageNum}
            onClick={() => onPageChange(pageNum)}
            className={`relative w-full aspect-[3/4] border rounded transition-all duration-200 overflow-hidden focus:outline-none focus:ring-2 focus:ring-blue-400 ${
              currentPage === pageNum
                ? 'border-blue-500 shadow-md'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="absolute inset-0 bg-gray-50 flex items-center justify-center">
              <Document
                file={sourceUrl}
                loading={null}
                error={null}
              >
                <Page
                  pageNumber={pageNum}
                  width={100}
                  renderTextLayer={false}
                  renderAnnotationLayer={false}
                />
              </Document>
            </div>
            <div className={`absolute bottom-0 inset-x-0 text-xs text-center py-1 ${
              currentPage === pageNum
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}>
              {pageNum}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};