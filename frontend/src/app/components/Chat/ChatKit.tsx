'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Loader2, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/Button';
import { aiApi } from '@/utils/api';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

interface ChatKitProps {
  onTaskAction?: () => void; // Callback when task is created/updated/deleted
}

export const ChatKit: React.FC<ChatKitProps> = ({ onTaskAction }) => {
  const [messages, setMessages] = useState<Message[]>([{
    id: 'welcome',
    role: 'agent',
    content: 'Hi! I\'m TaskFlow AI. How can I help you today?',
    timestamp: new Date(),
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = async (e: React.FormEvent, quickMessage?: string) => {
    e.preventDefault();

    const messageToSend = quickMessage || input;
    if (!messageToSend.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageToSend,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setIsSending(true);

    try {
      const response = await aiApi.sendMessage({ message: messageToSend });

      // Small delay to make typing indicator feel natural
      await new Promise(resolve => setTimeout(resolve, 500));

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: response.data.response,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, agentMessage]);

      // If chatbot performed any actions (task created/updated/deleted), trigger dashboard refresh
      if (response.data.actions && response.data.actions.length > 0) {
        console.log('[ChatKit] ✅ Task action detected, refreshing dashboard...', response.data.actions);

        // CRITICAL: Trigger dashboard refresh IMMEDIATELY after action
        if (onTaskAction) {
          onTaskAction();
          console.log('[ChatKit] 🔄 Dashboard refresh callback triggered');
        } else {
          console.warn('[ChatKit] ⚠️ No onTaskAction callback provided!');
        }
      } else {
        console.log('[ChatKit] ℹ️ No task actions in response');
      }
    } catch (error) {
      console.error('Failed to send message:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: '⚠️ Sorry, I encountered an error. Please try again or try a different request.',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  const handleQuickAction = (message: string) => {
    const fakeEvent = new Event('submit') as any;
    handleSendMessage(fakeEvent, message);
  };

  return (
    <div className="flex flex-col h-full bg-background-subtle rounded-lg border border-border overflow-hidden shadow-2xl">
      {/* Chat Header */}
      <div className="px-4 py-3 border-b border-border bg-gradient-to-r from-background to-accent-orange/5">
        <div className="flex items-center gap-3">
          <motion.div
            className="relative p-2 rounded-lg bg-accent-orange/10"
            animate={isLoading ? {
              boxShadow: [
                '0 0 0 0 rgba(251, 146, 60, 0)',
                '0 0 0 10px rgba(251, 146, 60, 0.1)',
                '0 0 0 0 rgba(251, 146, 60, 0)',
              ]
            } : {}}
            transition={{ duration: 1.5, repeat: isLoading ? Infinity : 0 }}
          >
            <Bot className="w-5 h-5 text-accent-orange" />
            {isLoading && (
              <motion.div
                className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
              />
            )}
          </motion.div>
          <div>
            <h3 className="font-semibold text-text-primary flex items-center gap-2">
              TaskFlow AI
              <Sparkles className="w-3 h-3 text-accent-yellow" />
            </h3>
            <p className="text-xs text-text-muted">
              {isLoading ? 'Thinking...' : 'Ready to help you organize'}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Action Buttons - Always visible */}
      {!isLoading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-4 py-3 bg-background/50 border-b border-border/50"
        >
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleQuickAction('Add a task')}
              className="px-3 py-1.5 text-xs bg-accent-orange/10 hover:bg-accent-orange/20 text-accent-orange rounded-full transition-colors flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3" />
              Add Task
            </button>
            <button
              onClick={() => handleQuickAction('Show all my tasks')}
              className="px-3 py-1.5 text-xs bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-full transition-colors"
            >
              📋 Show
            </button>
            <button
              onClick={() => handleQuickAction('What can you do?')}
              className="px-3 py-1.5 text-xs bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 rounded-full transition-colors"
            >
              ✨ Help Me
            </button>
          </div>
        </motion.div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              className={`flex gap-3 ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {message.role === 'agent' && (
                <motion.div
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-orange/10 flex items-center justify-center ring-2 ring-accent-orange/20"
                  animate={index === messages.length - 1 && isLoading ? {
                    scale: [1, 1.1, 1],
                  } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Bot className="w-4 h-4 text-accent-orange" />
                </motion.div>
              )}

              <motion.div
                className={`max-w-[80%] rounded-lg px-4 py-2 shadow-lg ${
                  message.role === 'user'
                    ? 'bg-gradient-to-r from-accent-orange to-accent-orange/90 text-white'
                    : 'bg-background border border-border/50 backdrop-blur-sm'
                }`}
                whileHover={{ scale: 1.02 }}
                transition={{ type: 'spring', stiffness: 400, damping: 20 }}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                <p
                  className={`text-xs mt-1 ${
                    message.role === 'user'
                      ? 'text-white/70'
                      : 'text-text-muted'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </p>
              </motion.div>

              {message.role === 'user' && (
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-accent-yellow/20 to-accent-orange/20 flex items-center justify-center ring-2 ring-accent-yellow/30">
                  <UserIcon className="w-4 h-4 text-accent-yellow" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex gap-3"
          >
            <motion.div
              className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-orange/10 flex items-center justify-center ring-2 ring-accent-orange/20"
              animate={{
                boxShadow: [
                  '0 0 0 0 rgba(251, 146, 60, 0.7)',
                  '0 0 0 10px rgba(251, 146, 60, 0)',
                  '0 0 0 0 rgba(251, 146, 60, 0)',
                ],
              }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Bot className="w-4 h-4 text-accent-orange" />
            </motion.div>
            <div className="bg-background border border-border/50 rounded-lg px-4 py-3 shadow-lg">
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <Loader2 className="w-4 h-4 text-accent-orange" />
                </motion.div>
                <div className="flex gap-1">
                  <motion.span
                    className="w-2 h-2 bg-accent-orange/60 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  />
                  <motion.span
                    className="w-2 h-2 bg-accent-orange/60 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.span
                    className="w-2 h-2 bg-accent-orange/60 rounded-full"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form
        onSubmit={handleSendMessage}
        className="p-4 border-t border-border bg-gradient-to-r from-background to-background-subtle"
      >
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me to add a task, show tasks, or mark tasks done..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-xl border-2 border-border bg-background-subtle text-gray-800 dark:text-gray-200 placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent-orange/30 focus:border-accent-orange disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          />
          <motion.button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`px-5 py-3 rounded-xl font-medium transition-all duration-200 ${
              !input.trim() || isLoading
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-accent-orange to-accent-orange/80 text-white hover:from-accent-orange/90 hover:to-accent-orange/70 shadow-lg hover:shadow-accent-orange/20'
            }`}
            whileHover={!input.trim() || isLoading ? {} : { scale: 1.05 }}
            whileTap={!input.trim() || isLoading ? {} : { scale: 0.95 }}
          >
            {isSending ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
              >
                <Loader2 className="w-5 h-5" />
              </motion.div>
            ) : (
              <motion.div
                whileHover={{ x: 2, y: -2 }}
                transition={{ type: 'spring', stiffness: 400, damping: 10 }}
              >
                <Send className="w-5 h-5" />
              </motion.div>
            )}
          </motion.button>
        </div>
      </form>
    </div>
  );
};
