'use client';

import React, { useState } from 'react';
import {
  Bell,
  Search,
  RefreshCw,
  ExternalLink,
  Bot,
  Send,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';

interface HeaderProps {
  onTriggerPoll: () => Promise<void>;
  isPolling: boolean;
  botOnline: boolean;
}

export function Header({ onTriggerPoll, isPolling, botOnline }: HeaderProps) {
  const [notificationOpen, setNotificationOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-[#1f2233] bg-[#090a10]/80 px-6 backdrop-blur-md">
      {/* Left: Quick Search */}
      <div className="flex items-center gap-3 w-72">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            placeholder="Search matching roles, companies..."
            className="h-9 w-full rounded-xl border border-[#23263b] bg-[#11121d] pl-9 pr-4 text-xs text-zinc-200 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Right: Actions & User Info */}
      <div className="flex items-center gap-3">
        {/* Telegram Bot Link Pill */}
        <a
          href="https://t.me/MyFuckingJobAlertbot"
          target="_blank"
          rel="noreferrer"
          className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border border-sky-500/30 bg-sky-500/10 text-xs font-medium text-sky-400 hover:bg-sky-500/20 transition-colors"
        >
          <Bot className="h-3.5 w-3.5" />
          <span>@MyFuckingJobAlertbot</span>
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        </a>

        {/* Manual Poll Trigger Button */}
        <button
          onClick={onTriggerPoll}
          disabled={isPolling}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 px-3.5 py-2 text-xs font-medium text-white shadow-md shadow-indigo-600/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isPolling ? 'animate-spin' : ''}`} />
          <span>{isPolling ? 'Scraping Sources...' : 'Run Scraper Now'}</span>
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setNotificationOpen(!notificationOpen)}
            className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-[#23263b] bg-[#11121d] text-zinc-300 hover:bg-[#181a29] transition-colors"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute top-2 right-2 h-2 w-2 rounded-full bg-indigo-500 ring-2 ring-[#090a10]" />
          </button>

          {notificationOpen && (
            <div className="absolute right-0 mt-2 w-80 rounded-2xl border border-[#24273d] bg-[#11121e] p-4 shadow-2xl backdrop-blur-xl z-50">
              <div className="flex items-center justify-between pb-3 border-b border-[#202338]">
                <h4 className="text-xs font-semibold text-white">Notifications</h4>
                <span className="text-[10px] text-zinc-400">Real-time alerts</span>
              </div>
              <div className="py-2 space-y-2">
                <div className="rounded-lg bg-[#161828] p-2.5 text-xs">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-medium">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    <span>Telegram Bot Connected</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    Token verified. Ready to push alerts to @MyFuckingJobAlertbot.
                  </p>
                </div>
                <div className="rounded-lg bg-[#161828] p-2.5 text-xs">
                  <div className="flex items-center gap-1.5 text-indigo-400 font-medium">
                    <Send className="h-3.5 w-3.5" />
                    <span>Scraper Active</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 mt-1">
                    LinkedIn, RemoteOK, and WWR feeds are healthy.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Avatar */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-[#1f2233]">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-600 font-bold text-xs text-white shadow-md">
            AA
          </div>
          <div className="hidden md:flex flex-col">
            <span className="text-xs font-semibold text-zinc-200">Arwa Ahmed</span>
            <span className="text-[10px] text-zinc-400">Junior React Dev</span>
          </div>
        </div>
      </div>
    </header>
  );
}
