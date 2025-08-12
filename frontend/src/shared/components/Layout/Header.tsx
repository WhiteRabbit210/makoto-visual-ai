import React from 'react';
import { Search, Bell, User } from 'lucide-react';

interface HeaderProps {
  title: string;
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
  return (
    <header className="h-16 bg-white border-b border-border px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-semibold text-text-primary">{title}</h2>
      </div>

      <div className="flex items-center gap-4">
        {/* Search */}
        <div className="relative">
          <input
            type="text"
            placeholder="検索..."
            className="w-64 px-4 py-2 pl-10 bg-bg-secondary rounded-lg border border-border 
              focus:outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/20 transition-all"
          />
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
        </div>

        {/* Notifications */}
        <button className="relative p-2 hover:bg-bg-hover rounded-lg transition-colors">
          <Bell className="w-5 h-5 text-text-secondary" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-status-error rounded-full"></span>
        </button>

        {/* User Menu */}
        <button className="flex items-center gap-2 p-2 hover:bg-bg-hover rounded-lg transition-colors">
          <div className="w-8 h-8 bg-primary-purple rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
        </button>
      </div>
    </header>
  );
};