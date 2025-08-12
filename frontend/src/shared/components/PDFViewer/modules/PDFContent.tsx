import React from 'react';
import { FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Document, Page } from 'react-pdf';

interface PDFContentProps {
  sourceId: string;
  sourceUrl: string;
  currentPage: number;
  pageWidth: number;
  zoom: number;
  onLoadSuccess: (sourceId: string, numPages: number) => void;
}

export const PDFContent: React.FC<PDFContentProps> = ({
  sourceId,
  sourceUrl,
  currentPage,
  pageWidth,
  zoom,
  onLoadSuccess
}) => {
  return (
    <div className="absolute inset-x-0 top-12 bottom-0 overflow-auto">
      <div className="min-h-full flex items-start justify-center p-4">
        <AnimatePresence mode="wait">
          <motion.div
            key={sourceId}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              transform: `scale(${zoom / 100})`,
              transformOrigin: 'center',
            }}
          >
            <Document
              file={sourceUrl}
              onLoadSuccess={(pdf) => onLoadSuccess(sourceId, pdf.numPages)}
              loading={
                <div className="text-center p-8">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-2 animate-pulse" />
                  <p className="text-sm text-gray-500">PDFを読み込み中...</p>
                </div>
              }
              error={
                <div className="text-center p-8">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-red-500">PDFの読み込みに失敗しました</p>
                </div>
              }
            >
              <div className="bg-white shadow-md">
                <Page
                  pageNumber={currentPage}
                  width={pageWidth * (zoom / 100)}
                  renderTextLayer={true}
                  renderAnnotationLayer={true}
                />
              </div>
            </Document>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};