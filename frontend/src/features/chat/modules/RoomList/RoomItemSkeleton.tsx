import React from 'react';

export const RoomItemSkeleton: React.FC = () => {
  return (
    <div className="px-3 py-3 rounded-lg">
      <div className="flex items-start gap-3 animate-pulse">
        {/* アバター */}
        <div className="w-10 h-10 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-full flex-shrink-0 animate-shimmer" />
        
        {/* コンテンツ */}
        <div className="flex-1 min-w-0">
          {/* タイトル */}
          <div className="h-4 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-3/4 mb-2 animate-shimmer" />
          
          {/* 最後のメッセージ */}
          <div className="space-y-1">
            <div className="h-3 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-full animate-shimmer" />
            <div className="h-3 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-5/6 animate-shimmer" />
          </div>
        </div>
        
        {/* タイムスタンプ */}
        <div className="h-3 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-12 flex-shrink-0 animate-shimmer" />
      </div>
    </div>
  );
};