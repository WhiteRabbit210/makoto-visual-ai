import React from 'react';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, Download, PanelLeftClose, PanelLeft, Maximize2, Maximize } from 'lucide-react';

interface ToolbarProps {
  showThumbnails: boolean;
  onToggleThumbnails: () => void;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  fitMode: 'width' | 'height' | null;
  onFitToWidth: () => void;
  onFitToHeight: () => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  downloadUrl: string;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  showThumbnails,
  onToggleThumbnails,
  currentPage,
  totalPages,
  onPageChange,
  fitMode,
  onFitToWidth,
  onFitToHeight,
  zoom,
  onZoomIn,
  onZoomOut,
  downloadUrl
}) => {
  return (
    <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-3 py-2 bg-white border-b border-gray-100 z-10" style={{ height: '48px' }}>
      <div className="flex items-center gap-1">
        <button
          onClick={onToggleThumbnails}
          className="p-1 rounded hover:bg-gray-100"
          title={showThumbnails ? 'サムネイルを非表示' : 'サムネイルを表示'}
        >
          {showThumbnails ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeft className="w-4 h-4" />}
        </button>
        <div className="w-px h-4 bg-gray-200 mx-1" />
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
        <span className="text-sm text-gray-600 px-2">
          {currentPage} / {totalPages}
        </span>
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      <div className="flex items-center gap-1">
        <div className="relative group">
          <button
            onClick={onFitToWidth}
            className={`p-1 rounded transition-colors ${
              fitMode === 'width' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
            }`}
            title="横幅に合わせる"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity">
            横幅に合わせる
            {fitMode === 'width' && ' (有効)'}
          </div>
        </div>
        <div className="relative group">
          <button
            onClick={onFitToHeight}
            className={`p-1 rounded transition-colors ${
              fitMode === 'height' ? 'bg-blue-100 text-blue-600' : 'hover:bg-gray-100'
            }`}
            title="高さに合わせる"
          >
            <Maximize className="w-4 h-4 rotate-90" />
          </button>
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity">
            高さに合わせる
            {fitMode === 'height' && ' (有効)'}
          </div>
        </div>
        <div className="w-px h-4 bg-gray-200 mx-1" />
        <button
          onClick={onZoomOut}
          className="p-1 rounded hover:bg-gray-100"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <span className="text-sm text-gray-600 w-12 text-center">
          {zoom}%
        </span>
        <button
          onClick={onZoomIn}
          className="p-1 rounded hover:bg-gray-100"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <div className="w-px h-4 bg-gray-200 mx-1" />
        <a
          href={downloadUrl}
          download
          className="p-1 rounded hover:bg-gray-100"
        >
          <Download className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
};