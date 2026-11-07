'use client';

import React from 'react';
import {
  Briefcase,
  Sparkles,
  Send,
  Radio,
  ArrowUpRight,
  TrendingUp,
} from 'lucide-react';
import { BotStats } from '@/types';

interface StatsGridProps {
  stats: BotStats;
}

export function StatsGrid({ stats }: StatsGridProps) {
  const cards = [
    {
      title: 'Jobs Found Today',
      value: stats.jobs_found_today,
      trend: '+4 in last 2h',
      subtext: `${stats.jobs_found_week} total this week`,
      icon: Briefcase,
      color: 'from-blue-500 to-indigo-600',
      badgeColor: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    },
    {
      title: 'AI Matches (>= 85%)',
      value: '9',
      trend: '64% match rate',
      subtext: 'Filtered for Junior React roles',
      icon: Sparkles,
      color: 'from-indigo-500 to-purple-600',
      badgeColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
    },
    {
      title: 'Telegram Alerts Sent',
      value: stats.alerts_sent,
      trend: 'Instant push',
      subtext: 'Pushed to @MyFuckingJobAlertbot',
      icon: Send,
      color: 'from-sky-500 to-cyan-600',
      badgeColor: 'text-sky-400 bg-sky-500/10 border-sky-500/20',
    },
    {
      title: 'Active Job Sources',
      value: `${stats.sources_active}/${stats.sources_total}`,
      trend: '100% online',
      subtext: 'LinkedIn, RemoteOK, WWR, Wuzzuf',
      icon: Radio,
      color: 'from-emerald-500 to-teal-600',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="group relative overflow-hidden rounded-2xl border border-[#212438] bg-[#11121e]/90 p-5 shadow-lg backdrop-blur-xl transition-all duration-300 hover:border-indigo-500/40 hover:-translate-y-1 hover:shadow-indigo-500/10"
          >
            {/* Top Row: Icon + Trend Badge */}
            <div className="flex items-center justify-between">
              <div
                className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-tr ${card.color} shadow-md`}
              >
                <Icon className="h-5 w-5 text-white" />
              </div>
              <span
                className={`flex items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-medium ${card.badgeColor}`}
              >
                <TrendingUp className="h-3 w-3" />
                {card.trend}
              </span>
            </div>

            {/* Middle: Number */}
            <div className="mt-4">
              <div className="text-2xl font-bold tracking-tight text-white group-hover:text-indigo-200 transition-colors">
                {card.value}
              </div>
              <div className="text-xs font-medium text-zinc-400 mt-0.5">
                {card.title}
              </div>
            </div>

            {/* Footer */}
            <div className="mt-3 pt-3 border-t border-[#1b1d2e] flex items-center justify-between text-[11px] text-zinc-500">
              <span>{card.subtext}</span>
              <ArrowUpRight className="h-3 w-3 text-zinc-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>
        );
      })}
    </div>
  );
}

