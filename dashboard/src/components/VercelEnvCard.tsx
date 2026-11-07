'use client';

import React, { useState } from 'react';
import {
  ExternalLink,
  Copy,
  Check,
  ShieldAlert,
  Server,
  Key,
  Layers,
} from 'lucide-react';

interface VercelEnvCardProps {
  token: string;
  chatId: string;
  cronSecret: string;
}

export function VercelEnvCard({ token, chatId, cronSecret }: VercelEnvCardProps) {
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);

  const envVars = [
    {
      key: 'TELEGRAM_TOKEN',
      value: token || '9219037439:AAHOQk7AuLgqyhOWGXlUXx17vV8W8kDkswU',
      desc: 'Bot HTTP API token for @MyFuckingJobAlertbot',
      required: true,
    },
    {
      key: 'TELEGRAM_CHAT_ID',
      value: chatId || 'YOUR_TELEGRAM_CHAT_ID',
      desc: 'Your personal Telegram account or channel Chat ID',
      required: true,
    },
    {
      key: 'CRON_SECRET',
      value: cronSecret || 'jobalert_secret_2026',
      desc: 'Protects /api/poll endpoint from unauthorized triggers',
      required: true,
    },
    {
      key: 'ANTHROPIC_API_KEY',
      value: 'sk-ant-api03-... (optional)',
      desc: 'Claude Sonnet key for automatic CV tailoring to DOCX',
      required: false,
    },
    {
      key: 'SMTP_USER',
      value: 'your.email@gmail.com (optional)',
      desc: 'Gmail address for email notifications',
      required: false,
    },
    {
      key: 'SMTP_APP_PASSWORD',
      value: 'your-16-char-app-password (optional)',
      desc: 'Gmail 2-Step Verification app password',
      required: false,
    },
  ];

  const fullEnvText = envVars
    .map((v) => `${v.key}=${v.value}`)
    .join('\n');

  const copyItem = (key: string, val: string) => {
    navigator.clipboard.writeText(val);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const copyAll = () => {
    navigator.clipboard.writeText(fullEnvText);
    setCopiedAll(true);
    setTimeout(() => setCopiedAll(false), 2000);
  };

  return (
    <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-6 shadow-xl backdrop-blur-xl">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-[#1f2233]">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-black border border-[#2c304a] shadow-lg">
            {/* Vercel Triangle Logo */}
            <svg
              className="h-5 w-5 text-white fill-current"
              viewBox="0 0 76 65"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M37.5274 0L75.0548 65H0L37.5274 0Z" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Vercel Environment Variables</h3>
            <p className="text-xs text-zinc-400">
              Target Project: <span className="font-semibold text-zinc-200">arrwa-s-projects / jobalert</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={copyAll}
            className="flex items-center gap-1.5 rounded-xl border border-indigo-500/30 bg-indigo-500/10 hover:bg-indigo-500/20 px-3 py-2 text-xs font-semibold text-indigo-300 transition-colors cursor-pointer"
          >
            {copiedAll ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{copiedAll ? 'Copied All .env' : 'Copy All for Vercel'}</span>
          </button>

          <a
            href="https://vercel.com/arrwa-s-projects/jobalert/settings/environment-variables"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-xl bg-white hover:bg-zinc-200 px-3.5 py-2 text-xs font-bold text-black shadow-md transition-colors"
          >
            <span>Open Vercel Settings</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>

      {/* Variables List */}
      <div className="mt-5 space-y-3">
        {envVars.map((item) => (
          <div
            key={item.key}
            className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 rounded-xl border border-[#202337] bg-[#0c0d16] p-3.5 hover:border-[#2b2f4a] transition-colors"
          >
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-indigo-300">
                  {item.key}
                </span>
                {item.required ? (
                  <span className="rounded bg-rose-500/15 border border-rose-500/30 px-1.5 py-0.2 text-[9px] font-bold uppercase tracking-wider text-rose-400">
                    Required
                  </span>
                ) : (
                  <span className="rounded bg-zinc-800 px-1.5 py-0.2 text-[9px] font-medium text-zinc-400">
                    Optional
                  </span>
                )}
              </div>
              <p className="text-[11px] text-zinc-500 mt-1">{item.desc}</p>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-zinc-400 max-w-xs truncate bg-[#141624] px-2.5 py-1 rounded border border-[#1d2033]">
                {item.value}
              </span>
              <button
                onClick={() => copyItem(item.key, item.value)}
                className="flex h-7 w-7 items-center justify-center rounded-lg border border-[#23273e] bg-[#161828] text-zinc-300 hover:bg-[#20233b] hover:text-white transition-colors cursor-pointer"
                title="Copy value"
              >
                {copiedKey === item.key ? (
                  <Check className="h-3 w-3 text-emerald-400" />
                ) : (
                  <Copy className="h-3 w-3" />
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Upstash Redis Reminder Box */}
      <div className="mt-5 rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-4 text-xs text-zinc-300">
        <div className="flex items-center gap-2 font-semibold text-indigo-300 mb-1">
          <Layers className="h-4 w-4" />
          <span>Important: Vercel Storage (Upstash Redis)</span>
        </div>
        <p className="text-[11px] text-zinc-400 leading-relaxed">
          On Vercel, go to the <strong className="text-zinc-200">Storage</strong> tab &rarr; Click <strong className="text-zinc-200">Create Database</strong> &rarr; Select <strong className="text-zinc-200">Upstash Redis (Free)</strong>. Vercel automatically populates <code className="text-sky-300">KV_REST_API_URL</code> and <code className="text-sky-300">KV_REST_API_TOKEN</code> so the bot never alerts you twice on the same job.
        </p>
      </div>
    </div>
  );
}

