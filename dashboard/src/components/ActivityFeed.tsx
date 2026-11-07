'use client';

import React, { useState, useEffect } from 'react';
import {
  Bell,
  Sparkles,
  Send,
  Radio,
  AlertTriangle,
  Clock,
} from 'lucide-react';
import { Activity } from '@/types';
import { timeAgo } from '@/lib/utils';

interface ActivityFeedProps {
  activities: Activity[];
}

function TimeAgoLabel({ timestamp }: { timestamp: string }) {
  const [label, setLabel] = useState<string>('recently');

  useEffect(() => {
    setLabel(timeAgo(timestamp));
  }, [timestamp]);

  return <span>{label}</span>;
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  const getIcon = (type: Activity['type']) => {
    switch (type) {
      case 'alert_sent':
        return <Send className="h-3.5 w-3.5 text-sky-400" />;
      case 'cv_generated':
        return <Sparkles className="h-3.5 w-3.5 text-purple-400" />;
      case 'job_found':
        return <Bell className="h-3.5 w-3.5 text-emerald-400" />;
      case 'error':
        return <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />;
      case 'poll':
      default:
        return <Radio className="h-3.5 w-3.5 text-indigo-400" />;
    }
  };

  const getDotBg = (type: Activity['type']) => {
    switch (type) {
      case 'alert_sent':
        return 'bg-sky-500/10 border-sky-500/30';
      case 'cv_generated':
        return 'bg-purple-500/10 border-purple-500/30';
      case 'job_found':
        return 'bg-emerald-500/10 border-emerald-500/30';
      case 'error':
        return 'bg-rose-500/10 border-rose-500/30';
      case 'poll':
      default:
        return 'bg-indigo-500/10 border-indigo-500/30';
    }
  };

  return (
    <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-5 shadow-lg backdrop-blur-xl">
      <div className="flex items-center justify-between pb-4 border-b border-[#1f2233]">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-bold text-white">Bot Activity Feed</h3>
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
        <span className="text-[11px] text-zinc-500 font-medium">Auto-updated</span>
      </div>

      <div className="mt-4 space-y-3.5">
        {activities.map((act) => (
          <div key={act.id} className="flex items-start gap-3 text-xs">
            {/* Icon Bubble */}
            <div
              className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border ${getDotBg(
                act.type
              )}`}
            >
              {getIcon(act.type)}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <p className="text-zinc-300 font-medium leading-snug">
                {act.message}
              </p>
              <div className="flex items-center gap-2 mt-1 text-[10px] text-zinc-500">
                <span className="flex items-center gap-1">
                  <Clock className="h-2.5 w-2.5" />
                  <TimeAgoLabel timestamp={act.timestamp} />
                </span>
                {act.source && (
                  <span className="rounded bg-[#1a1c2e] px-1.5 py-0.2 font-mono uppercase text-[9px] text-zinc-400">
                    {act.source}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
