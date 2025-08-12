import React, { useState, KeyboardEvent, useRef } from 'react';
import { InputActions } from './InputActions';
import { RichTextarea } from './RichTextarea';
import { AttachedFilesList } from '../FileAttachment';
import { TaskModal } from '../TaskModal';
import { TaskDisplay } from '../TaskDisplay';
import { ActiveModes, ActiveMode } from '../ActiveModes';
import { AgentButton } from './AgentButton';

interface MessageInputProps {
  onSendMessage: (content: string, files?: File[], modes?: string[]) => void;
  isLoading: boolean;
  onModesChange?: (modes: string[]) => void;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, isLoading, onModesChange }) => {
  const [message, setMessage] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [fileReferencesMap, setFileReferencesMap] = useState<Map<string, File>>(new Map());
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [currentTask, setCurrentTask] = useState<{ type: string; template: string; details: string } | null>(null);
  const [activeModes, setActiveModes] = useState<ActiveMode[]>([]);
  const [isAgentActive, setIsAgentActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if ((message.trim() || attachedFiles.length > 0) && !isLoading) {
      // アクティブモードのIDを抽出
      let modeIds = activeModes.map(m => m.id);
      
      // エージェントモードが有効な場合は追加
      if (isAgentActive) {
        modeIds = [...modeIds, 'agent'];
      }
      
      console.log('MessageInput - エージェントアクティブ:', isAgentActive);
      console.log('MessageInput - 送信モード:', modeIds);
      
      onSendMessage(message.trim(), attachedFiles, modeIds);
      setMessage('');
      setAttachedFiles([]);
      setFileReferencesMap(new Map());
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const newFiles = files.slice(0, 3 - attachedFiles.length); // 最大3ファイル
    setAttachedFiles([...attachedFiles, ...newFiles]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemoveFile = (index: number) => {
    const fileToRemove = attachedFiles[index];
    setAttachedFiles(attachedFiles.filter((_, i) => i !== index));
    
    // ファイル参照も削除
    const newMap = new Map(fileReferencesMap);
    newMap.delete(fileToRemove.name);
    setFileReferencesMap(newMap);
    
    // メッセージからファイル参照を削除
    const reference = `[${fileToRemove.name}]`;
    const newMessage = message.replace(reference, '');
    setMessage(newMessage);
  };

  const handleFileClick = (file: File) => {
    // ファイル参照をメッセージに追加
    const reference = `[${file.name}]`;
    if (!message.includes(reference)) {
      // カーソル位置に挿入したいが、今回は末尾に追加
      setMessage(message + (message.endsWith(' ') ? '' : ' ') + reference + ' ');
      
      // ファイル参照マップに追加
      const newMap = new Map(fileReferencesMap);
      newMap.set(file.name, file);
      setFileReferencesMap(newMap);
    }
  };

  const handleTaskSubmit = (taskType: string, template: string, details: string) => {
    setCurrentTask({ type: taskType, template, details });
    // タスクをメッセージに反映（必要に応じて）
    if (details) {
      setMessage(details);
    }
  };

  const handleModeToggle = (modeId: string) => {
    setActiveModes(prev => {
      const exists = prev.find(m => m.id === modeId);
      let newModes;
      if (exists) {
        newModes = prev.filter(m => m.id !== modeId);
      } else {
        // モードに応じて適切なアイコンを設定
        const modeConfig = {
          webcrawl: { name: 'Webクロール', icon: () => null, color: 'text-green-600', bgColor: 'bg-green-50' },
          image: { name: '画像生成', icon: () => null, color: 'text-purple-600', bgColor: 'bg-purple-50' },
          rag: { name: 'RAG', icon: () => null, color: 'text-blue-600', bgColor: 'bg-blue-50' }
        };
        const config = modeConfig[modeId as keyof typeof modeConfig] || { name: modeId, icon: () => null, color: '', bgColor: '' };
        newModes = [...prev, { id: modeId, ...config }];
      }
      // 親コンポーネントに通知
      if (onModesChange) {
        onModesChange(newModes.map(m => m.id));
      }
      return newModes;
    });
  };

  const handleRemoveMode = (modeId: string) => {
    setActiveModes(prev => {
      const newModes = prev.filter(m => m.id !== modeId);
      // 親コンポーネントに通知
      if (onModesChange) {
        onModesChange(newModes.map(m => m.id));
      }
      return newModes;
    });
  };

  return (
    <div className="glass-panel border-t border-border">
      {/* アクティブモード表示 */}
      <ActiveModes 
        activeModes={activeModes}
        onRemoveMode={handleRemoveMode}
      />
      
      {/* タスク表示 */}
      {currentTask && (
        <div className="px-4 pt-4">
          <TaskDisplay
            taskType={currentTask.type}
            taskTemplate={currentTask.template}
            taskDetails={currentTask.details}
            onClose={() => setCurrentTask(null)}
          />
        </div>
      )}
      
      {/* 添付ファイルリスト */}
      <AttachedFilesList
        files={attachedFiles}
        onRemove={handleRemoveFile}
        onFileClick={handleFileClick}
      />
      
      {/* 入力エリア */}
      <div className="p-4">
        <div className="flex items-center gap-2">
          {/* エージェントボタン */}
          <AgentButton
            isActive={isAgentActive}
            onClick={() => {
              const newAgentState = !isAgentActive;
              setIsAgentActive(newAgentState);
              
              // エージェントモードはアクティブモードに表示しない
              // ボタンの状態のみで管理
            }}
            disabled={isLoading}
          />
          
          <div className="flex-1 relative">
            <RichTextarea
              value={message}
              onChange={setMessage}
              onKeyPress={handleKeyPress}
              fileReferences={fileReferencesMap}
              disabled={isLoading}
            />
          </div>
          <InputActions 
            onSend={handleSend}
            isDisabled={!message.trim() && attachedFiles.length === 0}
            isLoading={isLoading}
            onAttachFile={() => fileInputRef.current?.click()}
            canAttachMore={attachedFiles.length < 3}
            onTaskSelect={() => setShowTaskModal(true)}
            currentTask={currentTask}
            onModeToggle={handleModeToggle}
            activeModes={activeModes.map(m => ({ id: m.id, label: m.name }))}
          />
        </div>
      </div>
      
      {/* 隠しファイル入力 */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        className="hidden"
        onChange={handleFileSelect}
        accept="*/*"
      />
      
      {/* タスク選択モーダル */}
      <TaskModal
        isOpen={showTaskModal}
        onClose={() => setShowTaskModal(false)}
        onSubmit={handleTaskSubmit}
      />
    </div>
  );
};