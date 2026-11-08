'use client';

import React, { useState, useMemo } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { StatsGrid } from '@/components/StatsGrid';
import { TelegramBotCard } from '@/components/TelegramBotCard';
import { FiltersPanel } from '@/components/FiltersPanel';
import { JobCard } from '@/components/JobCard';
import { JobModal } from '@/components/JobModal';
import { ActivityFeed } from '@/components/ActivityFeed';
import {
  INITIAL_STATS,
  INITIAL_CONFIG,
  INITIAL_JOBS,
  INITIAL_ACTIVITIES,
} from '@/lib/mock-data';
import { Job } from '@/types';
import { Briefcase } from 'lucide-react';

export default function DashboardPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [stats, setStats] = useState(INITIAL_STATS);
  const [config, setConfig] = useState(INITIAL_CONFIG);
  const [jobs, setJobs] = useState<Job[]>(INITIAL_JOBS);
  const [activities, setActivities] = useState(INITIAL_ACTIVITIES);
  const [isLoadingJobs, setIsLoadingJobs] = useState(false);

  // Filter States
  const [search, setSearch] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [workTypeFilter, setWorkTypeFilter] = useState('all');
  const [minScore, setMinScore] = useState(0);

  // Active Job for Modal
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Polling State
  const [isPolling, setIsPolling] = useState(false);

  // Fetch live jobs from Redis via API
  const fetchLiveJobs = async () => {
    try {
      setIsLoadingJobs(true);
      const res = await fetch('/api/jobs');
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.jobs) && data.jobs.length > 0) {
          setJobs(data.jobs);
          if (data.stats) {
            setStats(data.stats);
          }
        }
      }
    } catch (e) {
      console.warn('Failed to fetch live jobs:', e);
    } finally {
      setIsLoadingJobs(false);
    }
  };

  React.useEffect(() => {
    fetchLiveJobs();
  }, []);

  // Filter logic
  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      // Search term
      if (search.trim()) {
        const query = search.toLowerCase();
        const matchesTitle = job.title.toLowerCase().includes(query);
        const matchesComp = job.company.toLowerCase().includes(query);
        const matchesLoc = job.location.toLowerCase().includes(query);
        const matchesDesc = job.description.toLowerCase().includes(query);
        const matchesCountry = (job.country || '').toLowerCase().includes(query);
        if (!matchesTitle && !matchesComp && !matchesLoc && !matchesDesc && !matchesCountry) return false;
      }

      // Source filter
      if (selectedSource !== 'all' && job.source !== selectedSource) {
        return false;
      }

      // Work type filter
      if (workTypeFilter !== 'all') {
        const wt = (job.work_type || '').toLowerCase();
        if (workTypeFilter === 'remote' && !wt.includes('remote')) return false;
        if (workTypeFilter === 'hybrid' && !wt.includes('hybrid')) return false;
        if (workTypeFilter === 'onsite' && !wt.includes('on-site') && !wt.includes('onsite') && wt.includes('remote')) return false;
      }

      // Min score
      if (minScore > 0 && (job.match_score || 0) < minScore) {
        return false;
      }

      return true;
    });
  }, [jobs, search, selectedSource, workTypeFilter, minScore]);

  // Handle Manual Poll Trigger
  const handleTriggerPoll = async () => {
    setIsPolling(true);
    try {
      const res = await fetch('/api/poll');
      const data = await res.json();

      if (data.ok) {
        // Add new activity
        const newAct = {
          id: `act-${Date.now()}`,
          type: 'poll' as const,
          message: 'Manual scraping pass completed: verified all 7 job boards.',
          timestamp: new Date().toISOString(),
        };
        setActivities((prev) => [newAct, ...prev]);

        // Update stats
        setStats((prev) => ({
          ...prev,
          last_poll: new Date().toISOString(),
          jobs_found_today: prev.jobs_found_today + 1,
        }));

        // Refresh live jobs from Redis feed
        await fetchLiveJobs();
      }
    } catch {
      // silent fallback
    } finally {
      setIsPolling(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090a10] text-zinc-100 flex">
      {/* Sidebar Navigation */}
      <Sidebar
        collapsed={collapsed}
        setCollapsed={setCollapsed}
        botOnline={stats.is_online}
      />

      {/* Main Content Area */}
      <div
        className={`flex-1 transition-all duration-300 flex flex-col ${
          collapsed ? 'ml-20' : 'ml-64'
        }`}
      >
        {/* Top Header */}
        <Header
          onTriggerPoll={handleTriggerPoll}
          isPolling={isPolling}
          botOnline={stats.is_online}
        />

        {/* Dashboard Body */}
        <main className="flex-1 p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full">
          {/* Welcome & Live Status Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
                  JobAlert Dashboard
                </h1>
                <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                  Live Monitoring
                </span>
              </div>
              <p className="text-sm text-zinc-400 mt-1">
                Automated Junior React & Frontend job tracker with instant Telegram alerts and AI CV generation.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="rounded-xl border border-[#212438] bg-[#11121d] px-3.5 py-2 text-xs text-zinc-300 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-indigo-500" />
                <span>Last Polled: <strong>Just now</strong></span>
              </div>
            </div>
          </div>

          {/* 1. Key Metrics Cards */}
          <StatsGrid stats={stats} />

          {/* 2. Telegram Bot Integration Card */}
          <TelegramBotCard
            token={config.telegram_token}
            chatId={config.telegram_chat_id}
            setChatId={(newId) =>
              setConfig((prev) => ({ ...prev, telegram_chat_id: newId }))
            }
          />

          {/* 3. Job Feeds Section */}
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                  <Briefcase className="h-4 w-4" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white">
                    Matching Jobs Feed
                  </h2>
                  <p className="text-xs text-zinc-400">
                    Displaying {filteredJobs.length} junior frontend positions matching your criteria
                  </p>
                </div>
              </div>
            </div>

            {/* Filter Bar */}
            <FiltersPanel
              search={search}
              setSearch={setSearch}
              selectedSource={selectedSource}
              setSelectedSource={setSelectedSource}
              workTypeFilter={workTypeFilter}
              setWorkTypeFilter={setWorkTypeFilter}
              minScore={minScore}
              setMinScore={setMinScore}
            />

            {/* Jobs Cards Grid */}
            {filteredJobs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onOpenModal={(j) => setSelectedJob(j)}
                  />
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-[#212438] bg-[#11121d] p-12 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-[#171928] text-zinc-400 mb-3">
                  <Briefcase className="h-6 w-6" />
                </div>
                <h3 className="text-sm font-bold text-white">No matching jobs found</h3>
                <p className="text-xs text-zinc-500 mt-1 max-w-sm mx-auto">
                  Try adjusting your search filters or clearing the minimum match score.
                </p>
              </div>
            )}
          </div>

          {/* 4. Real-time Activity Feed */}
          <div>
            <ActivityFeed activities={activities} />
          </div>
        </main>
      </div>

      {/* Modal Dialog for AI Tailored CV & Referral */}
      <JobModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  );
}
