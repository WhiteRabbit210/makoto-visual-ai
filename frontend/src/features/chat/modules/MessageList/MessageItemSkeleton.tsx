import React from 'react';

interface MessageItemSkeletonProps {
  isUser?: boolean;
}

export const MessageItemSkeleton: React.FC<MessageItemSkeletonProps> = ({ isUser = false }) => {
  return (
    <div
      className={`flex items-start gap-3 ${
        isUser ? 'flex-row-reverse' : ''
      } animate-pulse`}
    >
      {/* アバター */}
      <div className="w-10 h-10 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-full flex-shrink-0 animate-shimmer" />
      
      {/* メッセージコンテンツ */}
      <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'} max-w-[80%]`}>
        {/* 名前 */}
        <div className="h-3 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-20 animate-shimmer" />
        
        {/* メッセージバブル */}
        <div
          className={`rounded-2xl p-4 ${
            isUser
              ? 'bg-gradient-to-r from-blue-100 to-blue-50 dark:from-blue-900/30 dark:to-blue-800/20'
              : 'bg-gradient-to-r from-gray-100 to-gray-50 dark:from-gray-800 dark:to-gray-700'
          }`}
        >
          <div className="space-y-2">
            <div className="h-4 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-600 dark:to-gray-500 rounded w-64 animate-shimmer" />
            <div className="h-4 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-600 dark:to-gray-500 rounded w-48 animate-shimmer" />
            <div className="h-4 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-600 dark:to-gray-500 rounded w-56 animate-shimmer" />
          </div>
        </div>
        
        {/* タイムスタンプ */}
        <div className="h-3 bg-gradient-to-r from-gray-300 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded w-24 mt-1 animate-shimmer" />
      </div>
    </div>
  );
};