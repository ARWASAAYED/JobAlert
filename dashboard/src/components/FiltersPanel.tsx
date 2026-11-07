'use client';

import React from 'react';
import { Search, Filter, Globe, Sparkles } from 'lucide-react';

interface FiltersPanelProps {
  search: string;
  setSearch: (v: string) => void;
  selectedSource: string;
  setSelectedSource: (v: string) => void;
  remoteOnly: boolean;
  setRemoteOnly: (v: boolean) => void;
  minScore: number;
  setMinScore: (v: number) => void;
}

export function FiltersPanel({
  search,
  setSearch,
  selectedSource,
  setSelectedSource,
  remoteOnly,
  setRemoteOnly,
  minScore,
  setMinScore,
}: FiltersPanelProps) {
  const sources = [
    { id: 'all', label: 'All Sources' },
    { id: 'linkedin', label: 'LinkedIn' },
    { id: 'remoteok', label: 'RemoteOK' },
    { id: 'wwr', label: 'WeWorkRemotely' },
    { id: 'wuzzuf', label: 'Wuzzuf' },
  ];

  return (
    <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-4 shadow-lg backdrop-blur-xl">
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by keyword (e.g. Next.js, Vodafone, Cairo)..."
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

        {/* Remote toggle & Score filter */}
        <div className="flex items-center gap-3 border-t lg:border-t-0 lg:border-l border-[#1f2233] pt-3 lg:pt-0 lg:pl-4">
          {/* Remote Only Toggle */}
          <button
            onClick={() => setRemoteOnly(!remoteOnly)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors cursor-pointer ${
              remoteOnly
                ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-300'
                : 'border-[#262940] bg-[#161828] text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Globe className="h-3.5 w-3.5" />
            <span>Remote Only</span>
          </button>

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
              <option value={85}>&ge; 85% Match</option>
              <option value={90}>&ge; 90% Match</option>
              <option value={95}>&ge; 95% Match</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
