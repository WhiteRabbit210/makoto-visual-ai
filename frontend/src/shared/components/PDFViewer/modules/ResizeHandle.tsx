import React from 'react';

interface ResizeHandleProps {
  isResizing: boolean;
  onResizeStart: (e: React.MouseEvent) => void;
}

export const ResizeHandle: React.FC<ResizeHandleProps> = ({ isResizing, onResizeStart }) => {
  return (
    <div
      className={`absolute bottom-0 left-0 right-0 h-2 cursor-ns-resize bg-gray-200 hover:bg-blue-200 transition-colors z-30 ${
        isResizing ? 'bg-blue-300' : ''
      }`}
      onMouseDown={onResizeStart}
    >
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-1 bg-gray-500 rounded-full" />
    </div>
  );
};