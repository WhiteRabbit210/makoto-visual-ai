import React, { useState, useEffect } from 'react';
import { RoomList } from '../modules/RoomList';
import { MessageList } from '../modules/MessageList';
import { MessageInput } from '../modules/MessageInput';
import { ActiveChatHeader } from '../modules/ChatHeader';
import { chatGPTApi } from '../../../core/api/chatgpt';
import { chatApi } from '../../../core/api/chat';
import { agentApi } from '../../../core/api/agent';
import type { ChatRoom, ChatMessage, StreamMessage, ChatMode, AnalyzeResponse } from '../../../types/api';
// import { webCrawlApi } from '../../../core/api/webcrawl'; // 現在未使用

/*
// Mock data
const mockChats = [
  {
    id: '1',
    title: 'ミツイワ社長について',
    lastMessage: 'ミツイワ株式会社の社長は誰ですか？',
    timestamp: '2025/07/09 12:23:19',
  },
  {
    id: '2',
    title: '議事録まとめ',
    lastMessage: 'これは議事録のまとめです...',
    timestamp: '2025/07/08 15:30:00',
  },
];

const mockMessagesData: { [key: string]: any[] } = {
  '1': [
    {
      id: '1',
      role: 'user' as const,
      content: 'ミツイワ株式会社の社長は誰ですか？',
      timestamp: '2025/07/09 12:23:19',
    },
    {
      id: '2',
      role: 'assistant' as const,
      content: `稲葉善典、ご質問をありがとうございます。
ミツイワ株式会社の現代表取締役社長は「高橋 洋章（たかはし ひろあき）」氏です。

参考情報をまとめると、以下の通りです：
• 高橋洋章氏は2023年1月1日付で代表取締役社長に就任されています。
• 1987年に愛知大学法経学部を卒業し、1998年にミツイワ株式会社に入社。
• 2012年に取締役、2022年に専務を歴任し、社長に就任されました。
• 前任の重本仁社長は退任されています。

以下の資料を参考にしました：`,
      timestamp: '2025/07/09 12:23:40',
      sources: [
        {
          id: 'pdf1',
          title: 'legal-20220125-jp-3.pdf',
          url: '/PDF/legal-20220125-jp-3.pdf',
          pages: 12
        },
        {
          id: 'pdf2',
          title: 'ミツイワ株式会社_年次報告書2023.pdf',
          url: '/PDF/annual-report-2023.pdf',
          pages: 48
        },
        {
          id: 'pdf3',
          title: '役員一覧_20230401.pdf',
          url: '/PDF/board-members-20230401.pdf',
          pages: 3
        },
        {
          id: 'pdf4',
          title: 'プレスリリース_社長交代.pdf',
          url: '/PDF/press-release-ceo.pdf',
          pages: 2
        }
      ]
    },
  ],
  '2': [
    {
      id: '3',
      role: 'user' as const,
      content: '本日の議事録をまとめてください',
      timestamp: '2025/07/08 15:30:00',
    },
    {
      id: '4',
      role: 'assistant' as const,
      content: '議事録のまとめを作成します...',
      timestamp: '2025/07/08 15:30:30',
    },
  ],
};
*/

interface AgentThought {
  id: string;
  role: 'agent_thought';
  content: string;
  timestamp: string;
  status?: 'thinking' | 'analyzing' | 'searching' | 'crawling' | 'generating' | 'complete';
}

export const ChatPage: React.FC = () => {
  const [activeChat, setActiveChat] = useState<string | null>(null);
  const [chats, setChats] = useState<ChatRoom[]>([]);
  const [messages, setMessages] = useState<(ChatMessage | AgentThought)[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isChangingChat, setIsChangingChat] = useState(false);
  const [activeModes, setActiveModes] = useState<string[]>([]);
  const [lastUserMessageId, setLastUserMessageId] = useState<string | undefined>();
  const [isGeneratingImage, setIsGeneratingImage] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [offset, setOffset] = useState(0);
  const [totalChats, setTotalChats] = useState(0);
  const [isAgentThinking, setIsAgentThinking] = useState(false);
  const [agentAnalysisResult, setAgentAnalysisResult] = useState<AnalyzeResponse | null>(null);
  const [agentThinkingStatus, setAgentThinkingStatus] = useState<'analyzing' | 'searching' | 'crawling' | 'generating'>('analyzing');
  const LIMIT = 20;

  // チャット一覧を取得
  useEffect(() => {
    console.log('Chat component mounted, setting loadingMore to true');
    setLoadingMore(true); // 初回読み込み時もローディング状態にする
    loadChats();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadChats = async (loadMore = false) => {
    if (loadingMore && loadMore) return; // 追加読み込み時のみ重複チェック
    
    console.log('loadChats called:', { loadMore, loadingMore, chatsLength: chats.length });
    
    try {
      setLoadingMore(true);
      const currentOffset = loadMore ? offset : 0;
      const response = await chatApi.getChats(currentOffset, LIMIT);
      console.log('API response:', { chats: response.chats.length, hasMore: response.has_more });
      
      if (loadMore) {
        setChats(prev => [...prev, ...response.chats]);
      } else {
        setChats(response.chats);
      }
      
      setOffset(currentOffset + response.chats.length);
      setHasMore(response.has_more);
      setTotalChats(response.total);
      
      // 最初のチャットを選択
      if (!loadMore && response.chats.length > 0 && !activeChat) {
        handleChatSelect(response.chats[0].room_id);
      }
    } catch (error) {
      console.error('Failed to load chats:', error);
    } finally {
      setLoadingMore(false);
    }
  };
  
  const handleLoadMore = () => {
    if (hasMore && !loadingMore) {
      loadChats(true);
    }
  };

  const handleChatSelect = async (chatId: string) => {
    if (chatId === activeChat) return;
    
    setIsChangingChat(true);
    try {
      await chatApi.getChat(chatId);
      setTimeout(() => {
        setActiveChat(chatId);
        // TODO: チャットのメッセージを別途取得する必要がある
        setMessages([]);
        setCurrentChatId(chatId); // 既存のチャットIDを設定
        setIsChangingChat(false);
      }, 150);
    } catch (error) {
      console.error('Failed to load chat:', error);
      setIsChangingChat(false);
    }
  };

  const handleNewChat = () => {
    // 新しいチャット作成時は状態をリセット
    setIsChangingChat(true);
    setTimeout(() => {
      setActiveChat(null);
      setMessages([]);
      setCurrentChatId(null);
      setIsChangingChat(false);
    }, 150);
  };

  const handleDeleteChat = async (chatId: string) => {
    if (window.confirm('このチャットを削除しますか？')) {
      try {
        await chatApi.deleteChat(chatId);
        setChats(chats.filter(chat => chat.room_id !== chatId));
        if (activeChat === chatId) {
          setActiveChat(null);
          setMessages([]);
          setCurrentChatId(null);
        }
      } catch (error) {
        console.error('Failed to delete chat:', error);
      }
    }
  };

  const handleSendMessage = async (content: string, files?: File[], modes?: string[]) => {
    const userMessageId = Date.now().toString();
    const userMessage: ChatMessage = {
      message_id: userMessageId,
      user_id: 'current_user',  // TODO: 実際のユーザーIDを使用
      room_id: currentChatId || 'temp',
      role: 'user' as const,
      content,
      timestamp: new Date().toLocaleString('ja-JP'),
    };

    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setLastUserMessageId(userMessageId);
    setIsLoading(true);
    setIsStreaming(true);
    setStreamingContent('');
    
    // エージェントモードの処理
    let activeModesForApi = modes || activeModes || [];
    let webSearchKeywords: string[] = [];
    
    console.log('受信したモード:', modes);
    console.log('アクティブモード:', activeModes);
    console.log('統合モード:', activeModesForApi);
    console.log('エージェントモード含まれる?:', activeModesForApi.includes('agent'));
    
    if (activeModesForApi.includes('agent')) {
      // エージェントモードが有効な場合
      setIsAgentThinking(true);
      
      try {
        setAgentThinkingStatus('analyzing');
        // エージェントによるプロンプト分析
        const analysisResult = await agentApi.analyzePrompt({
          prompt: content,
          context: messages.slice(-6).map(m => ({ 
            role: m.role, 
            content: m.content 
          }))
        });
        
        console.log('エージェント分析結果:', analysisResult);
        
        // 分析結果を保存
        setAgentAnalysisResult(analysisResult);
        
        // 分析結果に基づいてモードを自動設定
        const recommendedModes: string[] = [];
        
        for (const mode of analysisResult.modes) {
          if (mode.confidence > 0.5 && mode.type !== 'none') {
            // web -> webcrawl にマッピング
            const modeMap: Record<string, string> = {
              'web': 'webcrawl',
              'image': 'image',
              'rag': 'rag'
            };
            const mappedMode = modeMap[mode.type];
            if (mappedMode && !recommendedModes.includes(mappedMode)) {
              recommendedModes.push(mappedMode);
              
              // Webモードの場合は検索キーワードを保存
              if (mode.type === 'web' && mode.search_keywords) {
                webSearchKeywords = mode.search_keywords;
              }
            }
          }
        }
        
        // 推奨モードを追加（エージェントモードは保持）
        activeModesForApi = [...new Set([...activeModesForApi, ...recommendedModes])];
        
        // どのエージェントが選択されたかをログ出力（デバッグ用）
        console.log('🤖 エージェント分析完了!');
        console.log('選択されたモード:', recommendedModes);
        if (webSearchKeywords.length > 0) {
          console.log('検索キーワード:', webSearchKeywords);
          setAgentThinkingStatus('searching');
        }
        if (recommendedModes.includes('image')) {
          setAgentThinkingStatus('generating');
        }
        console.log('最終的なアクティブモード:', activeModesForApi);
        console.log('Web検索キーワード:', webSearchKeywords);
        
        // 分析完了後、1秒後に思考表示を非表示
        setTimeout(() => {
          setIsAgentThinking(false);
          setAgentAnalysisResult(null);
        }, 1500);
        
        // Webクロールはバックエンドで実行されるため、ここでは何もしない
        if (recommendedModes.includes('webcrawl') && webSearchKeywords.length > 0) {
          console.log('Webクロールはバックエンドで実行されます');
        }
        
      } catch (error) {
        console.error('エージェント分析エラー:', error);
      } finally {
        setIsAgentThinking(false);
      }
    }

    try {
      // メッセージ履歴をストリーミングAPIの形式に変換（agent_thoughtを除外）
      const streamMessages: StreamMessage[] = newMessages
        .filter(msg => msg.role !== 'agent_thought' || (msg as AgentThought).status === 'user')
        .map(msg => ({
          role: (msg.role === 'agent_thought' ? 'user' : msg.role) as 'user' | 'assistant',
          content: msg.content,
          timestamp: msg.timestamp
        }));

      // ストリーミング形式でChatGPT APIを呼び出し
      let aiContent = '';
      let generatedImages: Array<{url: string; prompt?: string; created_at?: string}> = [];
      let searchKeywords: string[] = [];
      let crawlSourcesFromApi: Array<{url: string; title: string; snippet: string}> = [];
      
      // エージェントが推奨したWeb検索キーワードを取得
      if (activeModesForApi.includes('webcrawl') && webSearchKeywords && webSearchKeywords.length > 0) {
        searchKeywords = webSearchKeywords;
      }
      
      await chatGPTApi.streamMessage(
        {
          messages: streamMessages,
          temperature: 0.7,
          max_tokens: 1000,
          modes: activeModesForApi as ChatMode[],
          stream: true as const,
          chat_id: currentChatId || undefined,
          search_keywords: searchKeywords
        },
        {
          onChunk: (chunk: string) => {
            aiContent += chunk;
            setStreamingContent(aiContent);
          },
          onDone: (returnedChatId?: string, crawlSources?: Array<{url: string; title: string; snippet: string}>) => {
            // ストリーミング完了
            if (returnedChatId) {
              if (!currentChatId) {
                setCurrentChatId(returnedChatId);
                console.log('新しいチャットが作成されました:', returnedChatId);
                // チャット一覧を更新
                loadChats(); // チャット一覧をリロード
              } else {
                console.log('メッセージが保存されました');
              }
            }
            
            // クロールソースを保存
            if (crawlSources && crawlSources.length > 0) {
              crawlSourcesFromApi = crawlSources;
              console.log('Webクロール参照元:', crawlSources.length, '件');
            }
            
            const aiMessage: AgentThought = {
              id: (Date.now() + 1).toString(),
              role: 'agent_thought',
              content: aiContent,
              timestamp: new Date().toLocaleString('ja-JP'),
              status: 'assistant'
            };
            setMessages(prev => [...prev, aiMessage]);
            setIsLoading(false);
            setIsStreaming(false);
            setStreamingContent('');
            setIsGeneratingImage(false);
          },
          onImage: (images: any) => {
            console.log('画像が生成されました:', images);
            generatedImages = images;
            setIsGeneratingImage(false);
            // 画像生成完了のテキストは追加しない（画像自体が表示される）
          },
          onGeneratingImage: () => {
            console.log('画像生成中...');
            setIsGeneratingImage(true);
          },
          onImageError: (error: any) => {
            console.error('画像生成エラー:', error);
            setIsGeneratingImage(false);
            setStreamingContent(prev => prev + `\n\n[画像生成エラー: ${error}]`);
          },
          onAgentThought: (thought: string, status: string) => {
            const thoughtMessage: AgentThought = {
              id: `thought-${Date.now()}`,
              role: 'agent_thought',
              content: thought,
              timestamp: new Date().toLocaleString('ja-JP'),
              status
            };
            setMessages(prev => [...prev, thoughtMessage]);
          },
          onAgentStatus: (status: any) => {
            // 既存のステータス処理と互換性を保つ
            if (status.status === 'analyzing') {
              setAgentThinkingStatus('analyzing');
            } else if (status.status === 'searching') {
              setAgentThinkingStatus('searching');
            } else if (status.status === 'crawling') {
              setAgentThinkingStatus('crawling');
            }
          }
        }
      );
    } catch (error) {
      console.error('ChatGPT API Error:', error);
      // エラー時のフォールバックメッセージ
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: `申し訳ございません、エラーが発生しました。しばらくしてから再度お試しください。${files?.length ? `添付ファイル: ${files.map(f => f.name).join(', ')}` : ''}`,
        timestamp: new Date().toLocaleString('ja-JP'),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      setIsStreaming(false);
      setStreamingContent('');
      setIsGeneratingImage(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Chat Room List */}
      <RoomList
        chats={chats.map(chat => ({
          id: chat.room_id,
          title: chat.title,
          lastMessage: chat.last_message || '',
          timestamp: new Date(chat.updated_at).toLocaleString('ja-JP')
        }))}
        activeChat={activeChat}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        onLoadMore={handleLoadMore}
        hasMore={hasMore}
        loadingMore={loadingMore}
        totalChats={totalChats}
      />

      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-transparent">
        {/* Chat Header */}
        <ActiveChatHeader 
          chatId={currentChatId || activeChat}
          chatTitle={chats.find(c => c.room_id === (currentChatId || activeChat))?.title}
        />
        
        {/* 新規チャット作成時も入力欄を表示 */}
        <>
          {/* Messages */}
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isChangingChat={isChangingChat}
            activeChat={activeChat}
            lastUserMessageId={lastUserMessageId}
            streamingContent={streamingContent}
            isStreaming={isStreaming}
            isGeneratingImage={isGeneratingImage}
            isAgentThinking={isAgentThinking}
            agentAnalysisResult={agentAnalysisResult}
            agentThinkingStatus={agentThinkingStatus}
          />

          {/* Input */}
          <MessageInput 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading}
            onModesChange={setActiveModes}
          />
        </>
      </div>
    </div>
  );
};