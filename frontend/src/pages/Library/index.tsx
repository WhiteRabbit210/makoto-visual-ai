import React from 'react';
import { TopBanner } from '../../components/Layout/TopBanner';
import { View, Edit, Trash2, Clock, User } from 'lucide-react';
import { motion } from 'framer-motion';

const mockData = [
  {
    id: '1',
    name: '議長',
    samples: 0,
    lastModified: '0秒',
    recognizedId: 'bd5d0a0f-91b4...',
    user: 'RecognizedID'
  },
  {
    id: '2',
    name: '話者111',
    samples: 1,
    lastModified: '5秒',
    recognizedId: '456214e0-77b4...',
    user: 'RecognizedID'
  }
];

export const LibraryPage: React.FC = () => {
  return (
    <div className="p-6">
      <TopBanner
        title="話者管理"
        subtitle="音声認識で使用する話者の登録と管理"
        onAction={() => console.log('Add speaker')}
        actionLabel="話者を追加"
      />

      <div className="bg-white rounded-xl border border-border">
        {/* Search Bar */}
        <div className="p-4 border-b border-border">
          <input
            type="text"
            placeholder="名前で検索..."
            className="w-full max-w-md px-4 py-2 bg-bg-secondary rounded-lg border border-border 
              focus:outline-none focus:border-primary-blue focus:ring-1 focus:ring-primary-blue/20"
          />
        </div>

        {/* Table Header */}
        <div className="grid grid-cols-6 gap-4 px-6 py-3 bg-bg-secondary border-b border-border text-sm font-medium text-text-secondary">
          <div>名前</div>
          <div>サンプル数</div>
          <div className="col-span-2">認識済みID</div>
          <div>最終変更</div>
          <div className="text-center">アクション</div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-border">
          {mockData.map((item, index) => (
            <motion.div 
              key={item.id} 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ backgroundColor: 'rgba(59, 130, 246, 0.02)' }}
              className="grid grid-cols-6 gap-4 px-6 py-4 items-center transition-all duration-200">
              <div className="flex items-center gap-2">
                <div className="w-10 h-10 bg-bg-secondary rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-text-muted" />
                </div>
                <span className="font-medium text-text-primary">{item.name}</span>
              </div>
              
              <div className="text-text-secondary">
                {item.samples} サンプル
              </div>
              
              <div className="col-span-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-text-muted">RecognizedID:</span>
                  <code className="text-xs bg-bg-secondary px-2 py-1 rounded">{item.recognizedId}</code>
                </div>
              </div>
              
              <div className="flex items-center gap-1 text-sm text-text-secondary">
                <Clock className="w-4 h-4" />
                {item.lastModified}
              </div>
              
              <div className="flex items-center justify-center gap-2">
                <motion.button 
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 hover:bg-bg-secondary rounded-lg transition-all duration-200 hover:shadow-sm"
                >
                  <View className="w-4 h-4 text-text-secondary" />
                </motion.button>
                <motion.button 
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 hover:bg-bg-secondary rounded-lg transition-all duration-200 hover:shadow-sm"
                >
                  <Edit className="w-4 h-4 text-text-secondary" />
                </motion.button>
                <motion.button 
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  className="p-2 hover:bg-status-error/10 rounded-lg transition-all duration-200 hover:shadow-sm"
                >
                  <Trash2 className="w-4 h-4 text-status-error hover:text-status-error/80" />
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};