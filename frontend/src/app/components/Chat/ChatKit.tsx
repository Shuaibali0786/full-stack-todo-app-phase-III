'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User as UserIcon, Loader2, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { taskApi } from '@/utils/api';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

interface ChatKitProps {
  onTaskAction?: () => void;
}

// ─── Intent Detection ────────────────────────────────────────────────────────

type Intent = 'CREATE' | 'READ' | 'COMPLETE' | 'DELETE' | 'UPDATE' | 'HELP' | 'GREETING' | 'UNKNOWN';

function detectIntent(msg: string): Intent {
  const m = msg.toLowerCase().trim();

  // GREETING
  if (/^(hi|hello|hey|good morning|good afternoon|good evening|howdy|yo)\b/.test(m)) return 'GREETING';

  // HELP
  if (/\b(help|what can you do|how to use|guide|instructions|capabilities)\b/.test(m)) return 'HELP';

  // READ — check before CREATE to avoid "show" triggering create
  if (/\b(show|list|display|view|see|get)\b/.test(m) && /\btasks?\b/.test(m)) return 'READ';
  if (/\bmy tasks?\b/.test(m) || /\ball tasks?\b/.test(m)) return 'READ';

  // DELETE
  if (/\b(delete|remove|cancel|erase|get rid of)\b/.test(m)) return 'DELETE';

  // COMPLETE
  if (/\b(complete|finish|done|mark( as)? (done|complete|finished)|check off)\b/.test(m)) return 'COMPLETE';

  // UPDATE
  if (/\b(update|change|rename|edit|modify)\b/.test(m) && /\bto\b/.test(m)) return 'UPDATE';

  // CREATE — explicit keywords or activity phrases
  if (/\b(add|create|new|make)\b/.test(m) && /\btask\b/.test(m)) return 'CREATE';
  if (/\b(remind me|remember to|i need to|i have to|i should|i will|i'll|going to|plan to)\b/.test(m)) return 'CREATE';
  if (/\b(tomorrow|tonight|today|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b/.test(m)) return 'CREATE';
  if (/\b(buy|call|email|send|write|read|meeting|appointment|schedule|submit|fix|pick up|drop off)\b/.test(m)) return 'CREATE';

  return 'UNKNOWN';
}

// ─── Title Extraction ─────────────────────────────────────────────────────────

function extractTitle(msg: string): string {
  let m = msg.toLowerCase().trim();

  // Strip command words
  const strip = [
    'add task', 'create task', 'new task', 'make task', 'add a task',
    'remind me to', 'remind me', 'remember to', 'remember',
    'i need to', 'i have to', 'i should', 'i must', 'i will', "i'll",
    'i am going to', "i'm going to", 'going to', 'plan to',
    'add', 'create', 'new', 'make',
  ];
  for (const s of strip) {
    if (m.startsWith(s + ' ') || m === s) {
      m = m.slice(s.length).trim();
      break;
    }
  }

  // Strip date suffixes
  m = m.replace(/\b(tomorrow|today|tonight|next week|next month|on (monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b.*$/i, '').trim();

  return m || msg.trim();
}

// ─── Task Identifier Extraction ───────────────────────────────────────────────

function extractIdentifier(msg: string, command: string[]): string {
  let m = msg.toLowerCase().trim();
  for (const c of command) {
    if (m.startsWith(c + ' ') || m === c) {
      m = m.slice(c.length).trim();
      break;
    }
  }
  // Strip leading articles
  m = m.replace(/^(the|a|an|my) /, '').trim();
  return m;
}

// ─── Task Fuzzy Finder ────────────────────────────────────────────────────────

interface TaskItem {
  id: string;
  title: string;
  is_completed: boolean;
  created_at: string;
  due_date?: string | null;
}

function findTask(identifier: string, tasks: TaskItem[]): TaskItem | null {
  if (!identifier) return null;
  const id = identifier.toLowerCase();

  // Exact short-ID match (first 8 chars of UUID)
  const byId = tasks.find(t => t.id.toLowerCase().startsWith(id));
  if (byId) return byId;

  // Exact title match
  const byTitle = tasks.find(t => t.title.toLowerCase() === id);
  if (byTitle) return byTitle;

  // Partial title match
  const partial = tasks.find(t => t.title.toLowerCase().includes(id) || id.includes(t.title.toLowerCase()));
  return partial || null;
}

// ─── Formatters ───────────────────────────────────────────────────────────────

function shortId(id: string) { return id.slice(0, 8); }

function formatTime(iso?: string) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch { return ''; }
}

// ─── Core Message Processor ──────────────────────────────────────────────────

async function processMessage(msg: string): Promise<{ response: string; acted: boolean }> {
  const intent = detectIntent(msg);

  if (intent === 'GREETING') {
    return {
      response: "Hi there! 👋 I'm TaskFlow AI. Try:\n• \"add task buy groceries\"\n• \"show my tasks\"\n• \"complete task [name]\"\n• \"delete task [name]\"",
      acted: false,
    };
  }

  if (intent === 'HELP') {
    return {
      response: "I'm TaskFlow AI 🤖 — your instant task assistant!\n\n✅ **Create**: \"add task buy groceries\"\n📋 **Show**: \"show my tasks\"\n✏️ **Update**: \"update task [name] to [new title]\"\n✅ **Complete**: \"complete task [name]\"\n❌ **Delete**: \"delete task [name]\"",
      acted: false,
    };
  }

  if (intent === 'READ') {
    const res = await taskApi.getTasks({ limit: 20, sort: 'created_at', order: 'desc' });
    const tasks: TaskItem[] = res.data?.tasks ?? res.data ?? [];
    const pending = tasks.filter((t: TaskItem) => !t.is_completed);

    if (pending.length === 0) {
      return { response: "🎉 You have no pending tasks! Type \"add task [title]\" to create one.", acted: false };
    }

    const emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟'];
    const lines = pending.slice(0, 10).map((t: TaskItem, i: number) =>
      `${emojis[i] ?? `${i+1})`} (${shortId(t.id)}) ${t.title} – ${formatTime(t.created_at)}`
    );
    return {
      response: `📋 **Your ${pending.length} pending task${pending.length === 1 ? '' : 's'}:**\n\n${lines.join('\n')}\n\nSay "complete task [name or ID]" to mark one done.`,
      acted: false,
    };
  }

  if (intent === 'CREATE') {
    const title = extractTitle(msg);
    if (!title || title.length < 2) {
      return { response: "❓ What should I name the task? Try: \"add task buy groceries\"", acted: false };
    }
    const res = await taskApi.createTask({ title });
    const task = res.data;
    return {
      response: `✅ Task created!\n\n📝 **${task.title}**\nID: ${shortId(task.id)}\nCreated: ${formatTime(task.created_at)}\n\nYour dashboard has been updated!`,
      acted: true,
    };
  }

  if (intent === 'COMPLETE') {
    const identifier = extractIdentifier(msg, ['complete task', 'finish task', 'mark done', 'mark as done', 'mark task done', 'done with', 'complete', 'finish', 'done']);
    const res = await taskApi.getTasks({ limit: 100 });
    const tasks: TaskItem[] = res.data?.tasks ?? res.data ?? [];
    const pending = tasks.filter((t: TaskItem) => !t.is_completed);
    const task = findTask(identifier, pending);

    if (!task) {
      const names = pending.slice(0, 5).map((t: TaskItem) => `• ${t.title} (${shortId(t.id)})`).join('\n');
      return { response: `❓ Task not found. Your pending tasks:\n${names || 'None'}`, acted: false };
    }

    await taskApi.toggleTaskComplete(task.id, true);
    return {
      response: `🎉 Task completed!\n\n✅ **${task.title}**\n\nGreat job! One less thing to worry about 💪`,
      acted: true,
    };
  }

  if (intent === 'DELETE') {
    const identifier = extractIdentifier(msg, ['delete task', 'remove task', 'cancel task', 'delete the task', 'delete', 'remove', 'cancel', 'erase']);
    const res = await taskApi.getTasks({ limit: 100 });
    const tasks: TaskItem[] = res.data?.tasks ?? res.data ?? [];
    const task = findTask(identifier, tasks);

    if (!task) {
      const names = tasks.slice(0, 5).map((t: TaskItem) => `• ${t.title} (${shortId(t.id)})`).join('\n');
      return { response: `❓ Task not found. Your tasks:\n${names || 'None'}`, acted: false };
    }

    await taskApi.deleteTask(task.id);
    return {
      response: `🗑️ Task deleted!\n\n**${task.title}**\n\nYour dashboard has been updated!`,
      acted: true,
    };
  }

  if (intent === 'UPDATE') {
    // Extract "task [identifier] to [new title]"
    const m = msg.toLowerCase().trim();
    const toIdx = m.lastIndexOf(' to ');
    if (toIdx === -1) {
      return { response: "❓ Try: \"update task [name] to [new title]\"", acted: false };
    }
    const newTitle = msg.trim().slice(toIdx + 4).trim();
    const rawBefore = m.slice(0, toIdx).trim();
    const identifier = extractIdentifier(rawBefore, ['update task', 'change task', 'rename task', 'edit task', 'modify task', 'update', 'change', 'rename', 'edit', 'modify']);

    const res = await taskApi.getTasks({ limit: 100 });
    const tasks: TaskItem[] = res.data?.tasks ?? res.data ?? [];
    const task = findTask(identifier, tasks);

    if (!task) {
      const names = tasks.slice(0, 5).map((t: TaskItem) => `• ${t.title} (${shortId(t.id)})`).join('\n');
      return { response: `❓ Task not found. Your tasks:\n${names || 'None'}`, acted: false };
    }

    const updated = await taskApi.updateTask(task.id, { title: newTitle });
    return {
      response: `✅ Task updated!\n\n📝 **${updated.data.title}**\nID: ${shortId(updated.data.id)}\n\nYour dashboard has been updated!`,
      acted: true,
    };
  }

  return {
    response: "❓ I'm not sure what you mean. Try:\n• \"add task buy groceries\"\n• \"show my tasks\"\n• \"complete task [name]\"\n• \"delete task [name]\"\n• \"update task [name] to [new title]\"",
    acted: false,
  };
}

// ─── Component ────────────────────────────────────────────────────────────────

export const ChatKit: React.FC<ChatKitProps> = ({ onTaskAction }) => {
  const [messages, setMessages] = useState<Message[]>([{
    id: 'welcome',
    role: 'agent',
    content: "Hi! I'm TaskFlow AI. How can I help you today?",
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

  useEffect(() => { scrollToBottom(); }, [messages]);
  useEffect(() => { inputRef.current?.focus(); }, []);

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

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setIsSending(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 400));

      const { response, acted } = await processMessage(messageToSend);

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);

      if (acted && onTaskAction) {
        onTaskAction();
      }
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Unknown error';
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: `⚠️ Something went wrong: ${detail}. Please try again.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
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
              boxShadow: ['0 0 0 0 rgba(251, 146, 60, 0)', '0 0 0 10px rgba(251, 146, 60, 0.1)', '0 0 0 0 rgba(251, 146, 60, 0)']
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

      {/* Quick Action Buttons */}
      {!isLoading && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-4 py-3 bg-background/50 border-b border-border/50"
        >
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => handleQuickAction('add task ')}
              className="px-3 py-1.5 text-xs bg-accent-orange/10 hover:bg-accent-orange/20 text-accent-orange rounded-full transition-colors flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3" />
              Add Task
            </button>
            <button
              onClick={() => handleQuickAction('show my tasks')}
              className="px-3 py-1.5 text-xs bg-blue-500/10 hover:bg-blue-500/20 text-blue-400 rounded-full transition-colors"
            >
              📋 Show
            </button>
            <button
              onClick={() => handleQuickAction('help')}
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
              className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.role === 'agent' && (
                <motion.div
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-orange/10 flex items-center justify-center ring-2 ring-accent-orange/20"
                  animate={index === messages.length - 1 && isLoading ? { scale: [1, 1.1, 1] } : {}}
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
                <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-white/70' : 'text-text-muted'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
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
              animate={{ boxShadow: ['0 0 0 0 rgba(251, 146, 60, 0.7)', '0 0 0 10px rgba(251, 146, 60, 0)', '0 0 0 0 rgba(251, 146, 60, 0)'] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <Bot className="w-4 h-4 text-accent-orange" />
            </motion.div>
            <div className="bg-background border border-border/50 rounded-lg px-4 py-3 shadow-lg">
              <div className="flex items-center gap-2">
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                  <Loader2 className="w-4 h-4 text-accent-orange" />
                </motion.div>
                <div className="flex gap-1">
                  {[0, 0.2, 0.4].map((delay, i) => (
                    <motion.span
                      key={i}
                      className="w-2 h-2 bg-accent-orange/60 rounded-full"
                      animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 1, repeat: Infinity, delay }}
                    />
                  ))}
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
            onChange={e => setInput(e.target.value)}
            placeholder="Ask me to add, show, complete, or delete tasks..."
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
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                <Loader2 className="w-5 h-5" />
              </motion.div>
            ) : (
              <motion.div whileHover={{ x: 2, y: -2 }} transition={{ type: 'spring', stiffness: 400, damping: 10 }}>
                <Send className="w-5 h-5" />
              </motion.div>
            )}
          </motion.button>
        </div>
      </form>
    </div>
  );
};
