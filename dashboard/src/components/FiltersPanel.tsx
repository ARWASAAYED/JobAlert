'use client';

import React from 'react';
import { Search, Globe, Sparkles, Building, Home, RefreshCw } from 'lucide-react';
import { WorkType } from '@/types';

interface FiltersPanelProps {
  search: string;
  setSearch: (v: string) => void;
  selectedSource: string;
  setSelectedSource: (v: string) => void;
  workTypeFilter: string;
  setWorkTypeFilter: (v: string) => void;
  minScore: number;
  setMinScore: (v: number) => void;
}

export function FiltersPanel({
  search,
  setSearch,
  selectedSource,
  setSelectedSource,
  workTypeFilter,
  setWorkTypeFilter,
  minScore,
  setMinScore,
}: FiltersPanelProps) {
  const sources = [
    { id: 'all', label: 'All Sources' },
    { id: 'linkedin', label: 'LinkedIn' },
    { id: 'indeed', label: 'Indeed' },
    { id: 'remoteok', label: 'RemoteOK' },
    { id: 'wwr', label: 'WWR' },
    { id: 'wuzzuf', label: 'Wuzzuf' },
    { id: 'remotive', label: 'Remotive' },
    { id: 'freehire', label: 'Freehire' },
    { id: 'jobicy', label: 'Jobicy' },
  ];

  const workTypes = [
    { id: 'all', label: 'All Types', icon: <Sparkles className="h-3 w-3" /> },
    { id: 'remote', label: 'Remote', icon: <Home className="h-3 w-3" /> },
    { id: 'hybrid', label: 'Hybrid', icon: <RefreshCw className="h-3 w-3" /> },
    { id: 'onsite', label: 'On-site', icon: <Building className="h-3 w-3" /> },
  ];

  return (
    <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-4 shadow-lg backdrop-blur-xl space-y-3">
      {/* Row 1: Search + Source pills */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by keyword (e.g. Next.js, Vodafone, Cairo, Germany)..."
            className="h-10 w-full rounded-xl border border-[#23263c] bg-[#0c0d16] pl-10 pr-4 text-xs text-zinc-100 placeholder-zinc-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Source Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          {sources.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelectedSource(s.id)}
              className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-all cursor-pointer ${
                selectedSource === s.id
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'bg-[#171928] text-zinc-400 hover:bg-[#20233b] hover:text-zinc-200'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      {/* Row 2: Work Type pills + Score filter */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-t border-[#1f2233] pt-3">
        {/* Work Type Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[11px] text-zinc-500 font-medium mr-1">Work Type:</span>
          {workTypes.map((wt) => (
            <button
              key={wt.id}
              onClick={() => setWorkTypeFilter(wt.id)}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors cursor-pointer ${
                workTypeFilter === wt.id
                  ? wt.id === 'remote'
                    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300'
                    : wt.id === 'hybrid'
                    ? 'border-amber-500/40 bg-amber-500/15 text-amber-300'
                    : wt.id === 'onsite'
                    ? 'border-sky-500/40 bg-sky-500/15 text-sky-300'
                    : 'border-indigo-500/40 bg-indigo-500/15 text-indigo-300'
                  : 'border-[#262940] bg-[#161828] text-zinc-400 hover:text-zinc-200'
              }`}
            >
              {wt.icon}
              <span>{wt.label}</span>
            </button>
          ))}
        </div>

        {/* Min Score Selector */}
        <div className="flex items-center gap-1.5 text-xs text-zinc-400">
          <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            aria-label="Filter jobs by minimum match score percentage"
            className="rounded-lg border border-[#262940] bg-[#161828] px-2.5 py-1.5 text-xs font-medium text-zinc-200 focus:border-indigo-500 focus:outline-none cursor-pointer"
          >
            <option value={0}>Any Score</option>
            <option value={50}>&ge; 50% Match</option>
            <option value={70}>&ge; 70% Match</option>
            <option value={85}>&ge; 85% Match</option>
            <option value={90}>&ge; 90% Match</option>
          </select>
        </div>
      </div>
    </div>
  );
}
