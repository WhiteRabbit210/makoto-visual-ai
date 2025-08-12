import React, { useState, useRef, useEffect } from 'react';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import { TabHeader, ThumbnailSidebar, Toolbar, PDFContent, ResizeHandle } from './modules';

// PDF.jsのワーカー設定
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface PDFSource {
  id: string;
  title: string;
  url: string;
  pages: number;
  currentPage?: number;
}

interface PDFViewerProps {
  sources: PDFSource[];
}

export const PDFViewer: React.FC<PDFViewerProps> = ({ sources }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [currentPages, setCurrentPages] = useState<{ [key: string]: number }>(
    sources.reduce((acc, source) => ({ ...acc, [source.id]: 1 }), {})
  );
  const [zoom, setZoom] = useState(100);
  const [numPages, setNumPages] = useState<{ [key: string]: number }>({});
  const [showThumbnails, setShowThumbnails] = useState(true);
  const [height, setHeight] = useState(700);
  const [isResizing, setIsResizing] = useState(false);
  const [pageWidth, setPageWidth] = useState(400);
  const contentRef = useRef<HTMLDivElement>(null);
  const [contentDimensions, setContentDimensions] = useState({ width: 0, height: 0 });
  const [fitMode, setFitMode] = useState<'width' | 'height' | null>('width');

  const handlePageChange = (sourceId: string, newPage: number) => {
    const maxPage = numPages[sourceId] || 1;
    if (newPage >= 1 && newPage <= maxPage) {
      setCurrentPages(prev => ({ ...prev, [sourceId]: newPage }));
    }
  };

  const onDocumentLoadSuccess = (sourceId: string, numPages: number) => {
    setNumPages(prev => ({ ...prev, [sourceId]: numPages }));
  };

  const activeSource = sources[activeTab];
  const currentPage = currentPages[activeSource?.id] || 1;
  const totalPages = numPages[activeSource?.id] || activeSource?.pages || 1;

  // コンテンツエリアのサイズを監視
  useEffect(() => {
    const updateDimensions = () => {
      if (contentRef.current) {
        const rect = contentRef.current.getBoundingClientRect();
        // ツールバー(48px) + パディング(32px) = 80px
        const toolbarHeight = 48;
        const padding = 32;
        const newDimensions = {
          width: rect.width - (showThumbnails ? 128 : 0) - padding, // サムネイル幅とパディングを引く
          height: rect.height - toolbarHeight - padding // ツールバー高さとパディングを引く
        };
        setContentDimensions(newDimensions);
        
        // フィットモードが有効な場合は自動的に再フィット
        if (fitMode === 'width' && newDimensions.width > 0) {
          setPageWidth(newDimensions.width);
          setZoom(100);
        } else if (fitMode === 'height' && newDimensions.height > 0) {
          const estimatedWidth = newDimensions.height * 0.707;
          setPageWidth(estimatedWidth);
          setZoom(100);
        }
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, [showThumbnails, height, fitMode]);

  // 横幅フィット
  const fitToWidth = () => {
    if (fitMode === 'width') {
      setFitMode(null);
      setPageWidth(400);
    } else {
      setFitMode('width');
      if (contentDimensions.width > 0) {
        setPageWidth(contentDimensions.width);
        setZoom(100);
      }
    }
  };

  // 高さフィット
  const fitToHeight = () => {
    if (fitMode === 'height') {
      setFitMode(null);
      setPageWidth(400);
    } else {
      setFitMode('height');
      if (contentDimensions.height > 0) {
        // PDFのアスペクト比を考慮（A4: 210×297mm ≈ 0.707）
        const estimatedWidth = contentDimensions.height * 0.707;
        setPageWidth(estimatedWidth);
        setZoom(100);
      }
    }
  };

  const handleResizeStart = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    const startY = e.clientY;
    const startHeight = height;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaY = e.clientY - startY;
      const newHeight = Math.max(300, Math.min(1200, startHeight + deltaY));
      setHeight(newHeight);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  return (
    <div 
      className="relative bg-white rounded-lg border border-gray-200 shadow-sm w-full"
      style={{ paddingBottom: '8px' }}
    >
      {/* タブヘッダー */}
      <TabHeader
        sources={sources}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* PDFビューエリア */}
      <div 
        ref={contentRef}
        className="relative bg-gray-50 flex overflow-hidden"
        style={{ height: `${height}px` }}
      >
        {/* サムネイルサイドバー */}
        {showThumbnails && activeSource && (
          <ThumbnailSidebar
            sourceUrl={activeSource.url}
            totalPages={totalPages}
            currentPage={currentPage}
            onPageChange={(pageNum) => handlePageChange(activeSource.id, pageNum)}
          />
        )}

        {/* メインビューエリア */}
        <div className="flex-1 relative">
          {/* ツールバー */}
          {activeSource && (
            <Toolbar
              showThumbnails={showThumbnails}
              onToggleThumbnails={() => setShowThumbnails(!showThumbnails)}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={(page) => handlePageChange(activeSource.id, page)}
              fitMode={fitMode}
              onFitToWidth={fitToWidth}
              onFitToHeight={fitToHeight}
              zoom={zoom}
              onZoomIn={() => {
                setFitMode(null);
                setZoom(Math.min(200, zoom + 10));
              }}
              onZoomOut={() => {
                setFitMode(null);
                setZoom(Math.max(50, zoom - 10));
              }}
              downloadUrl={activeSource.url}
            />
          )}

          {/* PDFコンテンツ */}
          {activeSource && (
            <PDFContent
              sourceId={activeSource.id}
              sourceUrl={activeSource.url}
              currentPage={currentPage}
              pageWidth={pageWidth}
              zoom={zoom}
              onLoadSuccess={onDocumentLoadSuccess}
            />
          )}
        </div>
      </div>
      
      {/* リサイズハンドル */}
      <ResizeHandle
        isResizing={isResizing}
        onResizeStart={handleResizeStart}
      />
    </div>
  );
};