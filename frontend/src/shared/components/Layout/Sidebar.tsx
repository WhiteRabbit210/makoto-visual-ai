import React, { useState } from 'react';
import { 
  ChevronLeft, 
  ChevronRight, 
  MessageSquare, 
  FolderOpen, 
  Mic, 
  Settings, 
  CheckSquare,
  Menu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const menuItems = [
  { id: 'chat', label: 'チャット', icon: MessageSquare },
  { id: 'library', label: 'ライブラリ管理', icon: FolderOpen },
  { id: 'audio', label: '音声ライブラリ', icon: Mic },
  { id: 'tasks', label: 'タスク管理', icon: CheckSquare },
  { id: 'settings', label: '設定', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleSidebar = () => setIsCollapsed(!isCollapsed);
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={toggleMobileMenu}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md"
      >
        <Menu className="w-6 h-6 text-text-primary" />
      </button>

      {/* Sidebar */}
      <AnimatePresence>
        <aside
          className={`
            fixed md:relative h-full glass-sidebar
            ${isMobileMenuOpen ? 'left-0' : '-left-full md:left-0'}
            transition-all duration-300 z-40
            ${isCollapsed ? 'w-20' : 'w-64'}
          `}
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-border min-h-[64px]">
              {!isCollapsed && (
                <h1 className="text-xl font-semibold text-text-primary whitespace-nowrap">
                  MAKOTO Visual
                </h1>
              )}
              <button
                onClick={toggleSidebar}
                className="hidden md:flex p-2 hover:bg-bg-hover rounded-lg transition-colors flex-shrink-0 ml-auto"
              >
                {isCollapsed ? (
                  <ChevronRight className="w-5 h-5 text-text-secondary" />
                ) : (
                  <ChevronLeft className="w-5 h-5 text-text-secondary" />
                )}
              </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4">
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;

                  return (
                    <motion.li 
                      key={item.id}
                      whileHover={{ x: isCollapsed ? 0 : 4 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <button
                        onClick={() => {
                          onTabChange(item.id);
                          setIsMobileMenuOpen(false);
                        }}
                        className={`
                          w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                          transition-all duration-200 group overflow-hidden
                          ${isActive 
                            ? 'bg-primary-blue text-white shadow-sm' 
                            : 'hover:bg-bg-hover hover:shadow-sm text-text-primary'
                          }
                        `}
                      >
                        <Icon className={`w-5 h-5 flex-shrink-0 transition-transform duration-200 ${
                          !isActive ? 'group-hover:scale-110' : ''
                        }`} />
                        {!isCollapsed && (
                          <span className="font-medium whitespace-nowrap overflow-hidden">{item.label}</span>
                        )}
                      </button>
                    </motion.li>
                  );
                })}
              </ul>
            </nav>

            {/* Footer */}
            <div className="p-4 border-t border-border">
              <div className={`text-xs text-text-muted ${isCollapsed ? 'text-center' : ''}`}>
                {isCollapsed ? 'v1.0' : 'Version 1.0.0'}
              </div>
            </div>
          </div>
        </aside>
      </AnimatePresence>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </>
  );
};