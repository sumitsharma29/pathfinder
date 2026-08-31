import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  User,
  Send,
  Plus,
  ExternalLink,
  BookOpen,
  Sparkles,
  MessageSquare,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { api } from '../api/client';
import {
  ConversationSummary,
  ConversationDetailData,
  ConversationMessage,
  CitationSource
} from '../types/api';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { LoadingSpinner } from '../components/common/FeedbackStates';

export const AssistantPage: React.FC = () => {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isSending, setIsSending] = useState<boolean>(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const loadConversations = async () => {
    try {
      const list = await api.getConversations();
      setConversations(list);
      if (list.length > 0 && !activeConversationId) {
        selectConversation(list[0].id);
      }
    } catch (e) {
      console.error('Failed to load conversations', e);
    }
  };

  const selectConversation = async (id: string) => {
    setActiveConversationId(id);
    setIsLoadingHistory(true);
    try {
      const detail = await api.getConversation(id);
      setMessages(detail.messages || []);
    } catch (e) {
      console.error('Failed to load conversation history', e);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || isSending) return;

    const userText = inputMessage.trim();
    setInputMessage('');

    // Append optimistic user message
    const tempUserMsg: ConversationMessage = {
      id: `temp-${Date.now()}`,
      sender: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsSending(true);

    try {
      const res = await api.sendAssistantMessage(
        userText,
        activeConversationId || undefined
      );

      // Append assistant response
      const assistantMsg: ConversationMessage = {
        id: res.message?.id || `msg-${Date.now()}`,
        sender: 'assistant',
        content: res.message?.content || (res as any).response || 'No response content generated.',
        created_at: res.message?.created_at || new Date().toISOString(),
        sources: res.sources || res.message?.sources || [],
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // If new conversation, update active ID and list
      if (!activeConversationId && res.conversation_id) {
        setActiveConversationId(res.conversation_id);
        await loadConversations();
      }
    } catch (err: any) {
      const errorMsg: ConversationMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        content: `Error: ${err.message || 'Failed to generate response. Please try again.'}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col md:flex-row gap-4 animate-in fade-in duration-300">
      {/* Sidebar: Conversation Threads */}
      <div className="w-full md:w-64 glass-panel rounded-2xl p-4 flex flex-col border border-slate-800 shrink-0">
        <Button onClick={handleNewChat} size="sm" className="w-full mb-4">
          <Plus className="w-4 h-4 mr-1.5" /> New Conversation
        </Button>

        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-2 mb-2">
          History
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 pr-1">
          {conversations.map((c) => (
            <button
              key={c.id}
              onClick={() => selectConversation(c.id)}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs transition flex items-center gap-2.5 truncate ${
                activeConversationId === c.id
                  ? 'bg-emerald-500/10 text-emerald-300 font-semibold border border-emerald-500/30'
                  : 'text-slate-400 hover:text-white hover:bg-slate-900 border border-transparent'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate">{c.title || 'Conversation'}</span>
            </button>
          ))}
          {conversations.length === 0 && (
            <p className="text-xs text-slate-500 p-2 text-center">No past chats yet</p>
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="flex-1 glass-panel rounded-2xl flex flex-col border border-slate-800 overflow-hidden">
        {/* Top Chat Header */}
        <div className="h-14 px-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-950 border border-emerald-800/80 flex items-center justify-center text-emerald-400">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
                PathFinder Learning Assistant
                <Badge variant="success" size="sm">
                  Grounded RAG
                </Badge>
              </h3>
            </div>
          </div>
          <span className="text-xs text-slate-400 hidden sm:inline">
            Answers verified with direct database citations
          </span>
        </div>

        {/* Message Stream */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          {messages.length === 0 && !isLoadingHistory && (
            <div className="text-center py-16 max-w-md mx-auto space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-950 border border-emerald-800/80 flex items-center justify-center mx-auto text-emerald-400">
                <Sparkles className="w-6 h-6" />
              </div>
              <h4 className="text-base font-bold text-white">Ask anything about your learning path</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                "Why is Linear Algebra a prerequisite for Machine Learning?"
                <br />
                "What resources will help me master Probability?"
              </p>
            </div>
          )}

          {isLoadingHistory && (
            <div className="py-12">
              <LoadingSpinner message="Loading messages..." size="md" />
            </div>
          )}

          {messages.map((msg) => {
            const isUser = msg.sender === 'user';

            return (
              <div
                key={msg.id}
                className={`flex gap-3 sm:gap-4 max-w-3xl ${
                  isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center text-xs font-semibold ${
                    isUser
                      ? 'bg-emerald-500 text-slate-950'
                      : 'bg-slate-800 border border-slate-700 text-emerald-400'
                  }`}
                >
                  {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </div>

                <div className="space-y-3">
                  <div
                    className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                      isUser
                        ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-100 rounded-tr-none'
                        : 'glass-card border border-slate-800 text-slate-200 rounded-tl-none'
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>

                  {/* Grounded Citation Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="p-3 bg-slate-900/90 rounded-xl border border-slate-800 space-y-2">
                      <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Grounded References & Citations:
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {msg.sources.map((src) => (
                          <a
                            key={src.resource_id}
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 bg-slate-950 hover:bg-slate-800/80 rounded-lg border border-slate-800 transition flex items-center justify-between text-xs text-slate-300 hover:text-white"
                          >
                            <span className="truncate pr-2 font-medium">{src.title}</span>
                            <ExternalLink className="w-3.5 h-3.5 shrink-0 text-emerald-400" />
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {isSending && (
            <div className="flex gap-3 max-w-xl">
              <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-emerald-400 shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="glass-card p-4 rounded-2xl rounded-tl-none border border-slate-800">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                  Retrieving grounded context & drafting response...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/80">
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Ask a question about skills, prerequisites, or learning material..."
              className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
            />
            <Button type="submit" isLoading={isSending} disabled={!inputMessage.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};
