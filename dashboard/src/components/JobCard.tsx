'use client';

import React from 'react';
import {
  Building2,
  MapPin,
  Clock,
  Sparkles,
  ExternalLink,
  FileText,
  Users,
  Globe,
  Home,
  RefreshCw,
} from 'lucide-react';
import { Job } from '@/types';
import { sourceBadgeColor, workTypeBadge } from '@/lib/utils';

interface JobCardProps {
  job: Job;
  onOpenModal: (job: Job) => void;
}

export function JobCard({ job, onOpenModal }: JobCardProps) {
  const badge = sourceBadgeColor(job.source);
  const wt = workTypeBadge(job.work_type);

  // Referral search URL
  const referralUrl = job.company
    ? `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
        job.company + ' frontend engineer'
      )}&network=%5B%22F%22%2C%22S%22%5D&origin=GLOBAL_SEARCH_HEADER`
    : null;

  return (
    <div className="group relative flex flex-col justify-between rounded-2xl border border-[#212438] bg-[#11121d] p-5 shadow-lg transition-all duration-300 hover:border-indigo-500/40 hover:-translate-y-1 hover:shadow-indigo-500/10">
      {/* Top Bar: Source badge + Work Type + Match Score */}
      <div>
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-1.5">
            {/* Source Badge */}
            <div
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-medium capitalize ${badge.bg} ${badge.text} ${badge.border}`}
            >
              <span className={`h-1.5 w-1.5 rounded-full ${badge.dot}`} />
              <span>{job.source}</span>
            </div>

            {/* Work Type Badge */}
            <div
              className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${wt.color}`}
            >
              <span>{wt.emoji}</span>
              <span>{wt.label}</span>
            </div>
          </div>

          {/* Match Score Badge */}
          {job.match_score && (
            <div className="flex items-center gap-1.5 rounded-full bg-indigo-500/15 border border-indigo-500/30 px-2.5 py-0.5 text-xs font-semibold text-indigo-300">
              <Sparkles className="h-3 w-3 text-indigo-400" />
              <span>{job.match_score}% Match</span>
            </div>
          )}
        </div>

        {/* Job Title */}
        <h3 className="mt-3 text-base font-bold text-white group-hover:text-indigo-200 transition-colors line-clamp-1">
          {job.title}
        </h3>

        {/* Company & Location & Country */}
        <div className="mt-2 space-y-1.5 text-xs text-zinc-400">
          <div className="flex items-center gap-1.5">
            <Building2 className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
            <span className="font-medium text-zinc-300">{job.company}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <MapPin className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
            <span className="truncate">{job.location}</span>
          </div>
          {job.country && (
            <div className="flex items-center gap-1.5">
              <Globe className="h-3.5 w-3.5 text-zinc-500 shrink-0" />
              <span className="font-medium text-zinc-300">{job.country}</span>
            </div>
          )}
        </div>

        {/* Matched Keywords Tags */}
        {job.matched_keywords && job.matched_keywords.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {job.matched_keywords.slice(0, 4).map((kw, i) => (
              <span
                key={i}
                className="rounded-md border border-[#262940] bg-[#161828] px-2 py-0.5 text-[10px] font-medium text-zinc-300"
              >
                {kw}
              </span>
            ))}
          </div>
        )}

        {/* Short description preview */}
        <p className="mt-3 text-xs text-zinc-400 line-clamp-2 leading-relaxed">
          {job.description}
        </p>
      </div>

      {/* Footer & Actions */}
      <div className="mt-4 pt-3.5 border-t border-[#1a1c2d] flex items-center justify-between gap-2">
        <div className="flex items-center gap-1 text-[11px] text-zinc-500">
          <Clock className="h-3 w-3" />
          <span>{job.posted_text}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Find Referral Button */}
          {referralUrl && (
            <a
              href={referralUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 rounded-lg border border-[#252840] bg-[#151726] hover:bg-[#1d2036] px-2 py-1.5 text-xs font-medium text-amber-300 transition-colors"
              title={`Find referral at ${job.company}`}
            >
              <Users className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Referral</span>
            </a>
          )}

          {/* View AI CV / Details Button */}
          <button
            onClick={() => onOpenModal(job)}
            className="flex items-center gap-1.5 rounded-lg border border-[#252840] bg-[#151726] hover:bg-[#1d2036] px-2.5 py-1.5 text-xs font-medium text-indigo-300 transition-colors cursor-pointer"
            title="View AI Tailored CV & Details"
          >
            <FileText className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">AI CV</span>
          </button>

          {/* Direct Apply Button */}
          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 transition-all"
          >
            <span>Apply</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
