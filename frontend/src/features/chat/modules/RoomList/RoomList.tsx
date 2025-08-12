import React, { useState } from 'react';
import { RoomItem } from './RoomItem';
import { RoomItemSkeleton } from './RoomItemSkeleton';
import { ChatHeader } from '../ChatHeader';
import { SearchBar } from '../SearchBar';

interface Chat {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: string;
}

interface RoomListProps {
  chats: Chat[];
  activeChat: string | null;
  onChatSelect: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
  onLoadMore?: () => void;
  hasMore?: boolean;
  loadingMore?: boolean;
}

export const RoomList: React.FC<RoomListProps> = ({
  chats,
  activeChat,
  onChatSelect,
  onNewChat,
  onDeleteChat,
  onLoadMore,
  hasMore = false,
  loadingMore = false,
}) => {
  console.log('RoomList render:', { chatsLength: chats.length, loadingMore });
  const [isEditMode, setIsEditMode] = useState(false);
  const [selectedChats, setSelectedChats] = useState<Set<string>>(new Set());

  const handleToggleEditMode = () => {
    setIsEditMode(!isEditMode);
    setSelectedChats(new Set());
  };

  const handleToggleSelect = (chatId: string) => {
    const newSelected = new Set(selectedChats);
    if (newSelected.has(chatId)) {
      newSelected.delete(chatId);
    } else {
      newSelected.add(chatId);
    }
    setSelectedChats(newSelected);
  };

  const handleDeleteSelected = () => {
    selectedChats.forEach(chatId => {
      onDeleteChat(chatId);
    });
    setSelectedChats(new Set());
    setIsEditMode(false);
  };

  return (
    <div className="w-80 glass-panel border-r border-border flex flex-col">
      {/* Header */}
      <ChatHeader
        isEditMode={isEditMode}
        selectedCount={selectedChats.size}
        onNewChat={onNewChat}
        onToggleEditMode={handleToggleEditMode}
        onBulkDelete={handleDeleteSelected}
      />

      {/* Search */}
      <div className="p-4 border-b border-border">
        <SearchBar onSearch={(query) => console.log('Search:', query)} />
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin" 
        onScroll={(e) => {
          const target = e.currentTarget;
          if (target.scrollHeight - target.scrollTop <= target.clientHeight + 100) {
            if (hasMore && !loadingMore && onLoadMore) {
              onLoadMore();
            }
          }
        }}
      >
        <div className="p-2 space-y-1">
          {/* チャットアイテム */}
          {chats.map((chat, index) => (
            <RoomItem
              key={chat.id}
              chat={chat}
              isActive={activeChat === chat.id}
              onClick={() => onChatSelect(chat.id)}
              onDelete={() => onDeleteChat(chat.id)}
              index={index}
              isEditMode={isEditMode}
              isSelected={selectedChats.has(chat.id)}
              onToggleSelect={() => handleToggleSelect(chat.id)}
            />
          ))}
          
          {/* 追加読み込み中のプレースホルダ */}
          {loadingMore && chats.length > 0 && (
            <>
              {[...Array(3)].map((_, i) => (
                <RoomItemSkeleton key={`skeleton-more-${i}`} />
              ))}
            </>
          )}
          
          {/* すべて読み込まれた場合 */}
          {!hasMore && chats.length > 0 && (
            <div className="py-4 text-center text-text-muted text-sm">
              すべてのチャットを表示しました
            </div>
          )}
        </div>
      </div>
      
      {/* チャット合計数表示 */}
      <div className="border-t border-border p-3 bg-surface/50">
        <p className="text-sm text-text-muted text-center">
          チャット: {chats.length}件
        </p>
      </div>
    </div>
  );
};