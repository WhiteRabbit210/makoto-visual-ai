import React, { useState } from 'react';
import { Layout } from './shared/components/Layout';
import { ChatPage } from './features/chat/pages/Chat';

const tabTitles: Record<string, string> = {
  chat: 'チャット',
  library: 'ライブラリ管理',
  audio: '音声ライブラリ管理',
  tasks: 'タスク管理',
  settings: '設定',
};

function App() {
  const [activeTab, setActiveTab] = useState('chat');

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatPage />;
      case 'library':
        return <div className="p-6">ライブラリ管理画面（実装中）</div>;
      case 'audio':
        return <div className="p-6">音声ライブラリ管理画面（実装中）</div>;
      case 'tasks':
        return <div className="p-6">タスク管理画面（実装中）</div>;
      case 'settings':
        return <div className="p-6">設定画面（実装中）</div>;
      default:
        return <ChatPage />;
    }
  };

  return (
    <Layout 
      activeTab={activeTab} 
      onTabChange={setActiveTab}
      title={tabTitles[activeTab]}
    >
      {renderContent()}
    </Layout>
  );
}

export default App;