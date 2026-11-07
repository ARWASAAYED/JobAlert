'use client';

import React, { useState, useMemo } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { FiltersPanel } from '@/components/FiltersPanel';
import { JobCard } from '@/components/JobCard';
import { JobModal } from '@/components/JobModal';
import { INITIAL_STATS, INITIAL_JOBS } from '@/lib/mock-data';
import { Job } from '@/types';
import { Briefcase, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function JobsPage() {
  const [collapsed, setCollapsed] = useState(false);
  const [jobs, setJobs] = useState<Job[]>(INITIAL_JOBS);
  const [search, setSearch] = useState('');
  const [selectedSource, setSelectedSource] = useState('all');
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [minScore, setMinScore] = useState(0);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      if (search.trim()) {
        const query = search.toLowerCase();
        const matchesTitle = job.title.toLowerCase().includes(query);
        const matchesComp = job.company.toLowerCase().includes(query);
        const matchesLoc = job.location.toLowerCase().includes(query);
        const matchesDesc = job.description.toLowerCase().includes(query);
        if (!matchesTitle && !matchesComp && !matchesLoc && !matchesDesc) return false;
      }
      if (selectedSource !== 'all' && job.source !== selectedSource) return false;
      if (remoteOnly && !job.remote) return false;
      if (minScore > 0 && (job.match_score || 0) < minScore) return false;
      return true;
    });
  }, [jobs, search, selectedSource, remoteOnly, minScore]);

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

        <main className="flex-1 p-6 md:p-8 space-y-6 max-w-7xl mx-auto w-full">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Link
                  href="/"
                  className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-white transition-colors"
                >
                  <ArrowLeft className="h-3.5 w-3.5" />
                  <span>Back to Overview</span>
                </Link>
              </div>
              <h1 className="mt-2 text-2xl font-extrabold text-white">
                Job Feed Explorer
              </h1>
              <p className="text-xs text-zinc-400">
                All junior developer positions captured across LinkedIn, RemoteOK, WeWorkRemotely, and Wuzzuf.
              </p>
            </div>

            <div className="text-xs font-semibold text-zinc-300 bg-[#11121d] border border-[#212438] px-3 py-1.5 rounded-xl">
              Showing {filteredJobs.length} results
            </div>
          </div>

          <FiltersPanel
            search={search}
            setSearch={setSearch}
            selectedSource={selectedSource}
            setSelectedSource={setSelectedSource}
            remoteOnly={remoteOnly}
            setRemoteOnly={setRemoteOnly}
            minScore={minScore}
            setMinScore={setMinScore}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onOpenModal={(j) => setSelectedJob(j)}
              />
            ))}
          </div>
        </main>
      </div>

      <JobModal
        job={selectedJob}
        onClose={() => setSelectedJob(null)}
      />
    </div>
  );
}
