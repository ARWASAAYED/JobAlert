'use client';

import React, { useState } from 'react';
import {
  Bot,
  Send,
  Search,
  CheckCircle2,
  AlertCircle,
  Copy,
  ExternalLink,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

interface TelegramBotCardProps {
  token: string;
  chatId: string;
  setChatId: (v: string) => void;
}

export function TelegramBotCard({ token, chatId, setChatId }: TelegramBotCardProps) {
  const [detecting, setDetecting] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: 'success' | 'error' | 'info';
    text: string;
  } | null>(null);
  const [copied, setCopied] = useState(false);

  const handleDetectChatId = async () => {
    setDetecting(true);
    setStatusMessage(null);
    try {
      const res = await fetch(`/api/telegram/get-chat-id?token=${encodeURIComponent(token)}`);
      const data = await res.json();

      if (data.ok && data.latest_chat_id) {
        setChatId(String(data.latest_chat_id));
        setStatusMessage({
          type: 'success',
          text: `Found Chat ID: ${data.latest_chat_id} from ${data.chats[0]?.name || 'your account'}!`,
        });
      } else {
        setStatusMessage({
          type: 'info',
          text: data.hint || 'No messages received yet. Please send /start to @MyFuckingJobAlertbot first in Telegram!',
        });
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to connect';
      setStatusMessage({
        type: 'error',
        text: message,
      });
    } finally {
      setDetecting(false);
    }
  };

  const handleSendTestAlert = async () => {
    if (!chatId) {
      setStatusMessage({
        type: 'error',
        text: 'Please detect or enter your Telegram Chat ID first.',
      });
      return;
    }

    setSendingTest(true);
    setStatusMessage(null);
    try {
      const res = await fetch('/api/telegram/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, chat_id: chatId }),
      });
      const data = await res.json();

      if (data.ok) {
        setStatusMessage({
          type: 'success',
          text: 'Alert sent! Check your Telegram @MyFuckingJobAlertbot right now.',
        });
      } else {
        setStatusMessage({
          type: 'error',
          text: data.error || 'Failed to send test alert.',
        });
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error sending message';
      setStatusMessage({
        type: 'error',
        text: message,
      });
    } finally {
      setSendingTest(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-2xl border border-[#212438] bg-gradient-to-b from-[#131524] to-[#0e101a] p-6 shadow-xl backdrop-blur-xl">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#1f2233]">
        <div className="flex items-center gap-3.5">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-tr from-sky-500 to-indigo-600 shadow-lg shadow-sky-500/20">
            <Bot className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">Telegram Alert Bot</h3>
              <span className="flex items-center gap-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-400">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Active
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Connected to <span className="font-mono text-sky-400">@MyFuckingJobAlertbot</span>
            </p>
          </div>
        </div>

        <a
          href="https://t.me/MyFuckingJobAlertbot"
          target="_blank"
          rel="noreferrer"
          className="flex items-center justify-center gap-2 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 px-3.5 py-2 text-xs font-medium text-sky-300 transition-colors"
        >
          <span>Open Bot in Telegram</span>
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>

      {/* Main Grid: Token & Chat ID */}
      <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Token Box */}
        <div className="rounded-xl border border-[#222538] bg-[#11121d] p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-zinc-300">HTTP API Token</span>
            <button
              onClick={() => handleCopy(token)}
              className="flex items-center gap-1 text-[11px] text-zinc-400 hover:text-indigo-300 transition-colors"
            >
              <Copy className="h-3 w-3" />
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
          <div className="font-mono text-xs text-zinc-400 bg-[#0b0c13] px-3 py-2 rounded-lg border border-[#1b1c2b] truncate">
            {token ? `${token.slice(0, 16)}••••••••••••••••••••••••` : 'No token provided'}
          </div>
          <p className="text-[10px] text-zinc-500 mt-2">
            Configured safely for Vercel production deployment.
          </p>
        </div>

        {/* Chat ID Box */}
        <div className="rounded-xl border border-[#222538] bg-[#11121d] p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-zinc-300">Telegram Chat ID</span>
            <span className="text-[10px] text-zinc-500">Your recipient ID</span>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={chatId}
              onChange={(e) => setChatId(e.target.value)}
              placeholder="e.g. 109283749"
              className="flex-1 rounded-lg border border-[#23263b] bg-[#0b0c13] px-3 py-1.5 font-mono text-xs text-zinc-200 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
            />
            <button
              onClick={handleDetectChatId}
              disabled={detecting}
              className="flex items-center gap-1.5 rounded-lg bg-[#1f2238] hover:bg-[#282c47] border border-[#2a2e4b] px-3 py-1.5 text-xs font-medium text-zinc-200 disabled:opacity-50 transition-colors"
            >
              <Search className={`h-3 w-3 ${detecting ? 'animate-spin' : ''}`} />
              <span>{detecting ? 'Checking...' : 'Auto-Detect'}</span>
            </button>
          </div>
          <p className="text-[10px] text-zinc-500 mt-2">
            Send <code className="text-sky-400">/start</code> to the bot, then click Auto-Detect.
          </p>
        </div>
      </div>

      {/* Action Bar & Test Dispatch */}
      <div className="mt-5 flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-[#1a1c2d]">
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <ShieldCheck className="h-4 w-4 text-emerald-400" />
          <span>Real-time instant push notifications enabled</span>
        </div>

        <button
          onClick={handleSendTestAlert}
          disabled={sendingTest}
          className="w-full sm:w-auto flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-sky-600/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          <Send className={`h-3.5 w-3.5 ${sendingTest ? 'animate-spin' : ''}`} />
          <span>{sendingTest ? 'Sending Test...' : 'Send Test Job Alert to Bot'}</span>
        </button>
      </div>

      {/* Status Feedback Banner */}
      {statusMessage && (
        <div
          className={`mt-4 flex items-center gap-2 rounded-xl p-3 text-xs border ${
            statusMessage.type === 'success'
              ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
              : statusMessage.type === 'error'
              ? 'border-rose-500/30 bg-rose-500/10 text-rose-300'
              : 'border-sky-500/30 bg-sky-500/10 text-sky-300'
          }`}
        >
          {statusMessage.type === 'success' ? (
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
          ) : (
            <AlertCircle className="h-4 w-4 shrink-0 text-sky-400" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}
    </div>
  );
}

