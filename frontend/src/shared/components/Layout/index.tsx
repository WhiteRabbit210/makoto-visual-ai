import React, { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
  title: string;
}

export const Layout: React.FC<LayoutProps> = ({ 
  children, 
  activeTab, 
  onTabChange,
  title 
}) => {
  return (
    <div className="flex h-screen relative">
      <Sidebar activeTab={activeTab} onTabChange={onTabChange} />
      
      <div className="flex-1 flex flex-col overflow-hidden relative z-10">
        <Header title={title} />
        
        <main className="flex-1 overflow-auto bg-transparent">
          {children}
        </main>
      </div>
    </div>
  );
};