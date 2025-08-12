import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronDown, Sparkles, FileText, Globe } from 'lucide-react';
import { taskTemplatesApi, TaskTemplate } from '../../../../core/api/taskTemplates';

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (taskType: string, template: string, details: string) => void;
}

const placeholderExample = `例：
• あなたは、優秀なライターです。会議で議論された主要なトピックと決定事項を要約して、わかりやすいメモを作成することができます。
• 要約は500文字以内で、各議論点についての簡潔な説明と、会議で合意されたアクションアイテムを含むものとします。`;

const getCategoryIcon = (category: string) => {
  switch (category) {
    case '作成':
      return FileText;
    case '分析':
      return Globe;
    default:
      return Sparkles;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case '作成':
      return 'text-blue-500 bg-blue-50 border-blue-200';
    case '分析':
      return 'text-green-500 bg-green-50 border-green-200';
    default:
      return 'text-purple-500 bg-purple-50 border-purple-200';
  }
};

const getCategoryBgColor = (category: string) => {
  switch (category) {
    case '作成':
      return 'bg-blue-50/50';
    case '分析':
      return 'bg-green-50/50';
    default:
      return 'bg-purple-50/50';
  }
};

export const TaskModal: React.FC<TaskModalProps> = ({ isOpen, onClose, onSubmit }) => {
  const [selectedTask, setSelectedTask] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [taskDetails, setTaskDetails] = useState('');
  const [isTemplateOpen, setIsTemplateOpen] = useState(false);
  const [taskTemplates, setTaskTemplates] = useState<TaskTemplate[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // タスクテンプレートを取得
  useEffect(() => {
    if (isOpen) {
      loadTaskTemplates();
    }
  }, [isOpen]);

  const loadTaskTemplates = async () => {
    setIsLoading(true);
    try {
      const templates = await taskTemplatesApi.getAllTemplates();
      setTaskTemplates(templates);
    } catch (error) {
      console.error('Failed to load task templates:', error);
      // エラー時はデフォルトのテンプレートを使用
      setTaskTemplates([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => {
    if (selectedTask || taskDetails) {
      onSubmit(selectedTask, selectedTemplate, taskDetails);
      // リセット
      setSelectedTask('');
      setSelectedTemplate('');
      setTaskDetails('');
      onClose();
    }
  };

  const handleTaskSelect = async (taskId: string) => {
    const template = taskTemplates.find(t => t.id === taskId);
    if (template) {
      setSelectedTask(taskId);
      setSelectedTemplate(template.name);
      setTaskDetails(template.prompt);
      setIsTemplateOpen(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* オーバーレイ */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* モーダル */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
          >
            <div className="bg-bg-primary rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
              {/* ヘッダー */}
              <div className="flex items-center justify-between p-6 border-b border-border bg-gradient-to-r from-primary-blue/5 to-purple-500/5">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary-blue/10 rounded-lg">
                    <Sparkles className="w-5 h-5 text-primary-blue" />
                  </div>
                  <h2 className="text-xl font-semibold text-text-primary">タスク設定</h2>
                </div>
                <button
                  type="button"
                  onClick={onClose}
                  className="p-2 hover:bg-bg-hover rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-text-secondary" />
                </button>
              </div>

              {/* コンテンツ */}
              <div className="p-6 space-y-6">
                {/* 説明文 */}
                <div className="bg-blue-50/50 rounded-lg p-4 border border-blue-100">
                  <p className="text-sm text-blue-700">
                    AIにあらかじめ覚えておてほしい事やルールを設定できます。
                  </p>
                  <p className="text-sm text-blue-600 mt-1">
                    タスクテンプレート設定後に編集を加えても、元データには影響はありません。
                  </p>
                </div>

                {/* 免責事項セクション */}
                <div className="bg-amber-50/50 rounded-lg p-4 border border-amber-100">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-amber-800">免責事項</h3>
                    <ChevronDown className="w-4 h-4 text-amber-600" />
                  </div>
                </div>

                {/* タスクテンプレート選択 */}
                <div>
                  <div className="text-sm font-medium text-text-secondary mb-2">
                    タスクをテンプレートから設定する
                  </div>
                  <div className="relative">
                    <button
                      type="button"
                      onClick={() => setIsTemplateOpen(!isTemplateOpen)}
                      className="w-full px-4 py-3 bg-gradient-to-r from-bg-secondary to-bg-secondary/50 border border-border rounded-lg text-left flex items-center justify-between hover:border-primary-blue/30 transition-all"
                    >
                      <span className={selectedTemplate ? 'text-text-primary font-medium' : 'text-text-muted'}>
                        {selectedTemplate || 'タスクを選択してください'}
                      </span>
                      <ChevronDown 
                        className={`w-5 h-5 text-text-muted transition-transform ${
                          isTemplateOpen ? 'rotate-180' : ''
                        }`}
                      />
                    </button>

                    {/* ドロップダウンメニュー */}
                    <AnimatePresence>
                      {isTemplateOpen && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className="absolute top-full left-0 right-0 mt-2 bg-white border border-border rounded-xl shadow-2xl z-10 overflow-hidden max-h-96 overflow-y-auto"
                        >
                          {isLoading ? (
                            <div className="p-4 text-center text-text-muted">
                              読み込み中...
                            </div>
                          ) : taskTemplates.length === 0 ? (
                            <div className="p-4 text-center text-text-muted">
                              タスクテンプレートがありません
                            </div>
                          ) : (
                            taskTemplates.map((task) => {
                              const Icon = getCategoryIcon(task.category);
                              const colorClass = getCategoryColor(task.category);
                              const bgColorClass = getCategoryBgColor(task.category);
                              const previewText = task.prompt.length > 80 
                                ? task.prompt.substring(0, 80) + '...' 
                                : task.prompt;
                              
                              return (
                                <button
                                  type="button"
                                  key={task.id}
                                  onClick={() => handleTaskSelect(task.id)}
                                  className={`w-full px-4 py-4 text-left hover:bg-bg-hover transition-all flex items-start gap-3 border-b border-border last:border-0 ${bgColorClass}`}
                                >
                                  <div className={`p-2.5 rounded-full border ${colorClass} flex-shrink-0`}>
                                    <Icon className="w-5 h-5" />
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                      <span className="font-medium text-text-primary text-base">
                                        {task.name}
                                      </span>
                                      <span className={`text-xs px-2 py-0.5 rounded-full ${colorClass} bg-opacity-20`}>
                                        {task.category}
                                      </span>
                                    </div>
                                    <div className="text-sm text-text-muted leading-relaxed">
                                      {previewText}
                                    </div>
                                  </div>
                                </button>
                              );
                            })
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>

                {/* 詳細入力エリア */}
                <div>
                  <div className="text-sm font-medium text-text-secondary mb-2">
                    タスクの詳細を入力してください
                  </div>
                  <div className="relative">
                    <textarea
                      value={taskDetails}
                      onChange={(e) => setTaskDetails(e.target.value)}
                      placeholder={placeholderExample}
                      className="w-full h-48 px-4 py-3 bg-gradient-to-r from-bg-secondary to-bg-secondary/50 border border-border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-blue/20 focus:border-primary-blue/30 transition-all placeholder:text-text-muted/60"
                    />
                    {selectedTask && (
                      <div className="absolute top-2 right-2">
                        <span className="text-xs px-2 py-1 bg-primary-blue/10 text-primary-blue rounded-full">
                          テンプレート適用済み
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* フッター */}
              <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-gradient-to-r from-bg-secondary/30 to-bg-secondary/10">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-6 py-2.5 text-text-secondary hover:text-text-primary transition-colors"
                >
                  閉じる
                </button>
                <button
                  type="button"
                  onClick={handleSubmit}
                  disabled={!selectedTask && !taskDetails}
                  className="px-6 py-2.5 bg-gradient-to-r from-primary-blue to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
                >
                  タスク設定
                </button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};