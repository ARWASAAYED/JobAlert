'use client';

import React, { useState } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { VercelEnvCard } from '@/components/VercelEnvCard';
import { TelegramBotCard } from '@/components/TelegramBotCard';
import { INITIAL_STATS, INITIAL_CONFIG } from '@/lib/mock-data';
import {
  Sliders,
  Check,
  Plus,
  Trash2,
  Clock,
  Globe,
  ExternalLink,
  ShieldCheck,
  Save,
} from 'lucide-react';
import Link from 'next/link';

export default function SettingsPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [config, setConfig] = useState(INITIAL_CONFIG);
  const [saved, setSaved] = useState(false);

  // New tag inputs
  const [newMust, setNewMust] = useState('');
  const [newExclude, setNewExclude] = useState('');

  const addMust = () => {
    if (newMust.trim() && !config.filters.title_must.includes(newMust.trim())) {
      setConfig({
        ...config,
        filters: {
          ...config.filters,
          title_must: [...config.filters.title_must, newMust.trim().toLowerCase()],
        },
      });
      setNewMust('');
    }
  };

  const removeMust = (word: string) => {
    setConfig({
      ...config,
      filters: {
        ...config.filters,
        title_must: config.filters.title_must.filter((w) => w !== word),
      },
    });
  };

  const addExclude = () => {
    if (newExclude.trim() && !config.filters.title_exclude.includes(newExclude.trim())) {
      setConfig({
        ...config,
        filters: {
          ...config.filters,
          title_exclude: [...config.filters.title_exclude, newExclude.trim().toLowerCase()],
        },
      });
      setNewExclude('');
    }
  };

  const removeExclude = (word: string) => {
    setConfig({
      ...config,
      filters: {
        ...config.filters,
        title_exclude: config.filters.title_exclude.filter((w) => w !== word),
      },
    });
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="min-h-screen bg-[#090a10] text-zinc-100 flex">
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        botOnline={INITIAL_STATS.is_online}
      />

      <div
        className={`flex-1 transition-all duration-300 flex flex-col ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        <Header
          onTriggerPoll={async () => {}}
          isPolling={false}
          botOnline={INITIAL_STATS.is_online}
        />

        <main className="flex-1 p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-extrabold text-white">
                Bot Settings & Vercel Configuration
              </h1>
              <p className="text-xs text-zinc-400 mt-1">
                Customize job search criteria, experience constraints, and Vercel cloud environment variables.
              </p>
            </div>

            <button
              onClick={handleSave}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 px-4 py-2 text-xs font-bold text-white shadow-lg shadow-indigo-600/25 transition-all cursor-pointer"
            >
              {saved ? <Check className="h-4 w-4" /> : <Save className="h-4 w-4" />}
              <span>{saved ? 'Settings Saved!' : 'Save Preferences'}</span>
            </button>
          </div>

          {/* 1. Telegram Connection */}
          <TelegramBotCard
            token={config.telegram_token}
            chatId={config.telegram_chat_id}
            setChatId={(newId) =>
              setConfig((prev) => ({ ...prev, telegram_chat_id: newId }))
            }
          />

          {/* 2. Job Filter Rules Card */}
          <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-6 shadow-xl backdrop-blur-xl space-y-6">
            <div className="flex items-center gap-3 pb-4 border-b border-[#1f2233]">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Sliders className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Matching Criteria & Keywords</h3>
                <p className="text-xs text-zinc-400">
                  Defines which jobs trigger instant Telegram alerts
                </p>
              </div>
            </div>

            {/* Title Must Include */}
            <div>
              <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 block mb-2">
                Job Title Must Contain Any Of:
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {config.filters.title_must.map((tag) => (
                  <span
                    key={tag}
                    className="flex items-center gap-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300"
                  >
                    <span>{tag}</span>
                    <button
                      onClick={() => removeMust(tag)}
                      className="text-indigo-400 hover:text-white"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2 max-w-md">
                <input
                  type="text"
                  value={newMust}
                  onChange={(e) => setNewMust(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addMust()}
                  placeholder="Add keyword (e.g. vue, tailwind)..."
                  className="flex-1 rounded-xl border border-[#23263c] bg-[#0c0d16] px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
                />
                <button
                  onClick={addMust}
                  className="flex items-center gap-1 rounded-xl bg-[#1d2035] hover:bg-[#262a47] px-3 py-2 text-xs font-medium text-zinc-200 border border-[#292d4b] transition-colors"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add</span>
                </button>
              </div>
            </div>

            {/* Title Must Exclude */}
            <div className="pt-4 border-t border-[#1f2233]">
              <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 block mb-2">
                Exclude Roles (Senior, Lead, Non-Frontend):
              </label>
              <div className="flex flex-wrap gap-2 mb-3">
                {config.filters.title_exclude.map((tag) => (
                  <span
                    key={tag}
                    className="flex items-center gap-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-300"
                  >
                    <span>{tag}</span>
                    <button
                      onClick={() => removeExclude(tag)}
                      className="text-rose-400 hover:text-white"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex gap-2 max-w-md">
                <input
                  type="text"
                  value={newExclude}
                  onChange={(e) => setNewExclude(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addExclude()}
                  placeholder="Add exclude keyword (e.g. devops, php)..."
                  className="flex-1 rounded-xl border border-[#23263c] bg-[#0c0d16] px-3.5 py-2 text-xs text-zinc-200 placeholder-zinc-600 focus:border-indigo-500 focus:outline-none"
                />
                <button
                  onClick={addExclude}
                  className="flex items-center gap-1 rounded-xl bg-[#1d2035] hover:bg-[#262a47] px-3 py-2 text-xs font-medium text-zinc-200 border border-[#292d4b] transition-colors"
                >
                  <Plus className="h-3.5 w-3.5" />
                  <span>Add</span>
                </button>
              </div>
            </div>

            {/* Max Years & Age Limit */}
            <div className="pt-4 border-t border-[#1f2233] grid grid-cols-1 sm:grid-cols-2 gap-6">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 block mb-1">
                  Maximum Experience Required: {config.filters.max_years} Years
                </label>
                <p className="text-[11px] text-zinc-500 mb-2">
                  Automatically skips postings demanding &gt; {config.filters.max_years} years.
                </p>
                <input
                  type="range"
                  min="0"
                  max="5"
                  step="1"
                  value={config.filters.max_years}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      filters: {
                        ...config.filters,
                        max_years: Number(e.target.value),
                      },
                    })
                  }
                  className="w-full accent-indigo-500 cursor-pointer"
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 block mb-1">
                  Freshness Window: {config.max_age_minutes} Minutes
                </label>
                <p className="text-[11px] text-zinc-500 mb-2">
                  Only alerts for posts published within this time frame.
                </p>
                <input
                  type="range"
                  min="10"
                  max="120"
                  step="5"
                  value={config.max_age_minutes}
                  onChange={(e) =>
                    setConfig({
                      ...config,
                      max_age_minutes: Number(e.target.value),
                    })
                  }
                  className="w-full accent-indigo-500 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* 3. Vercel Environment Variables Card */}
          <VercelEnvCard
            token={config.telegram_token}
            chatId={config.telegram_chat_id}
            cronSecret={config.cron_secret}
          />

          {/* 4. External Cron Schedule Guide */}
          <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-6 shadow-xl backdrop-blur-xl">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">
                  Recurring Schedule Setup (cron-job.org)
                </h3>
                <p className="text-xs text-zinc-400">
                  Keeps your bot continuously running every 2 minutes for free
                </p>
              </div>
            </div>

            <div className="space-y-3 text-xs text-zinc-300">
              <p>
                Because Vercel Hobby free tier only permits 1 scheduled cron run per day, use the free{' '}
                <a
                  href="https://cron-job.org"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-400 underline font-semibold"
                >
                  cron-job.org
                </a>{' '}
                service to ping your endpoint:
              </p>

              <div className="rounded-xl border border-[#22253c] bg-[#0c0d16] p-3 font-mono text-xs text-indigo-300 select-all">
                https://jobalert-arrwa-s-projects.vercel.app/api/poll?key={config.cron_secret}
              </div>

              <ul className="list-disc list-inside space-y-1 text-zinc-400 text-[11px] pt-1">
                <li>Schedule interval: Every 2 minutes</li>
                <li>HTTP Method: GET</li>
                <li>Response status expected: 200 OK</li>
              </ul>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

