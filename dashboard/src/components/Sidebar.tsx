'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Briefcase,
  Bot,
  Settings,
  Sparkles,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (v: boolean) => void;
  botOnline: boolean;
}

export function Sidebar({ collapsed, setCollapsed, botOnline }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    {
      name: 'Overview',
      href: '/',
      icon: LayoutDashboard,
    },
    {
      name: 'Job Feed',
      href: '/jobs',
      icon: Briefcase,
    },
    {
      name: 'Settings & Vercel',
      href: '/settings',
      icon: Settings,
    },
  ];

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 bottom-0 z-40 flex flex-col justify-between border-r border-[#1f2233] bg-[#0c0d16] transition-all duration-300',
        collapsed ? 'w-20' : 'w-64'
      )}
    >
      {/* Top Logo */}
      <div>
        <div className="flex h-16 items-center justify-between px-4 border-b border-[#1f2233]">
          {!collapsed ? (
            <Link href="/" className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-sky-500 shadow-lg shadow-indigo-500/25">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                  JobAlert <span className="text-[10px] uppercase font-bold tracking-widest px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">AI</span>
                </span>
                <span className="text-[11px] text-zinc-400">Telegram Bot Dashboard</span>
              </div>
            </Link>
          ) : (
            <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-600 to-sky-500 shadow-lg shadow-indigo-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
          )}
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-sm transition-all',
                  isActive
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                    : 'text-zinc-400 hover:text-zinc-100 hover:bg-[#151726]'
                )}
                title={collapsed ? item.name : undefined}
              >
                <Icon className={cn('h-5 w-5 shrink-0', isActive ? 'text-white' : 'text-zinc-400')} />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Bottom Bot Status & Collapse Button */}
      <div className="p-3 border-t border-[#1f2233] space-y-3">
        {/* Telegram Bot Indicator Card */}
        {!collapsed ? (
          <div className="rounded-xl border border-[#25283f] bg-[#121422] p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="relative flex h-2.5 w-2.5">
                  {botOnline && (
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  )}
                  <span
                    className={cn(
                      'relative inline-flex rounded-full h-2.5 w-2.5',
                      botOnline ? 'bg-emerald-500' : 'bg-rose-500'
                    )}
                  ></span>
                </div>
                <span className="text-xs font-semibold text-zinc-200">Telegram Bot</span>
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Online
              </span>
            </div>
            <p className="text-[11px] text-zinc-400 truncate font-mono">
              @MyFuckingJobAlertbot
            </p>
            <a
              href="https://t.me/MyFuckingJobAlertbot"
              target="_blank"
              rel="noreferrer"
              className="mt-2.5 flex items-center justify-center gap-1.5 w-full py-1.5 rounded-lg text-xs font-medium bg-indigo-500/15 hover:bg-indigo-500/25 text-indigo-300 border border-indigo-500/25 transition-colors"
            >
              <span>Open in Telegram</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        ) : (
          <div className="flex justify-center" title="Telegram Bot Online">
            <div className="h-3 w-3 rounded-full bg-emerald-500 ring-4 ring-emerald-500/20" />
          </div>
        )}

        {/* Toggle Collapse */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-9 w-full items-center justify-center rounded-lg bg-[#151726] hover:bg-[#1d2035] text-zinc-400 hover:text-zinc-200 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </button>
      </div>
    </aside>
  );
}
