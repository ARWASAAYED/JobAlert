'use client';

import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Building2,
  MapPin,
  Globe,
  ExternalLink,
  Copy,
  Check,
  FileText,
  UserCheck,
  Users,
  Home,
  RefreshCw,
  Building,
} from 'lucide-react';
import { Job } from '@/types';
import { workTypeBadge } from '@/lib/utils';

interface JobModalProps {
  job: Job | null;
  onClose: () => void;
}

export function JobModal({ job, onClose }: JobModalProps) {
  const [copiedNote, setCopiedNote] = useState(false);
  const [copiedMsg, setCopiedMsg] = useState(false);

  if (!job) return null;

  const wt = workTypeBadge(job.work_type);

  const connectionNote = `Hi [Name], I noticed you work at ${job.company}. I'm Arwa Ahmed, a Junior Frontend Developer specializing in React and Next.js. I recently saw the ${job.title} opening and would love to connect!`;

  const referralMessage = `Hi [Name], hope you're having a great week! I recently applied for the ${job.title} position at ${job.company}. As a Junior React developer with hands-on experience in Next.js, TypeScript, and modern web applications, I believe my skills match well with what your team is building. Would you be open to providing a referral or putting me in touch with the hiring manager? My CV is attached. Thank you so much!`;

  const referralSearchUrl = job.company
    ? `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
        job.company + ' frontend engineer'
      )}&network=%5B%22F%22%2C%22S%22%5D&origin=GLOBAL_SEARCH_HEADER`
    : null;

  const recruiterSearchUrl = job.company
    ? `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
        job.company + ' recruiter OR talent acquisition'
      )}&network=%5B%22F%22%2C%22S%22%5D&origin=GLOBAL_SEARCH_HEADER`
    : null;

  const managerSearchUrl = job.company
    ? `https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
        job.company + ' engineering manager'
      )}&network=%5B%22F%22%2C%22S%22%5D&origin=GLOBAL_SEARCH_HEADER`
    : null;

  const handleCopyNote = () => {
    navigator.clipboard.writeText(connectionNote);
    setCopiedNote(true);
    setTimeout(() => setCopiedNote(false), 2000);
  };

  const handleCopyMsg = () => {
    navigator.clipboard.writeText(referralMessage);
    setCopiedMsg(true);
    setTimeout(() => setCopiedMsg(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
      <div className="relative w-full max-w-2xl max-h-[90vh] overflow-hidden rounded-3xl border border-[#272a42] bg-[#11121e] shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-[#212439] p-6 bg-[#131525]">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-full">
                AI Match Score: {job.match_score || 0}%
              </span>
              {job.verdict && (
                <span className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                  job.verdict === 'Strong Fit' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                  job.verdict === 'Good Fit' ? 'text-blue-400 bg-blue-500/10 border-blue-500/20' :
                  'text-amber-400 bg-amber-500/10 border-amber-500/20'
                }`}>
                  {job.verdict}
                </span>
              )}
              <span className="text-xs text-zinc-400 font-medium">via {job.source}</span>
            </div>
            <h2 className="mt-2 text-xl font-bold text-white leading-snug">
              {job.title}
            </h2>
            <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-zinc-400">
              <span className="flex items-center gap-1.5 text-zinc-300 font-medium">
                <Building2 className="h-3.5 w-3.5 text-indigo-400" />
                {job.company}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin className="h-3.5 w-3.5 text-zinc-500" />
                {job.location}
              </span>
              {job.country && (
                <span className="flex items-center gap-1.5 text-zinc-300">
                  <Globe className="h-3.5 w-3.5 text-zinc-500" />
                  {job.country}
                </span>
              )}
              <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${wt.color}`}>
                {wt.emoji} {wt.label}
              </span>
            </div>
          </div>

          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1b1e32] text-zinc-400 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 text-sm">
          {/* Keywords Match Card */}
          <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-2.5 flex items-center gap-2">
              <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
              <span>Keyword Analysis</span>
            </h4>
            <div className="space-y-2">
              <div>
                <span className="text-[11px] text-zinc-400 block mb-1">
                  Matched in Your Profile:
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {(job.matched_keywords || ['React', 'Next.js', 'TypeScript', 'Tailwind']).map((k, i) => (
                    <span
                      key={i}
                      className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-300"
                    >
                      ✓ {k}
                    </span>
                  ))}
                </div>
              </div>

              {job.missing_keywords && job.missing_keywords.length > 0 && (
                <div className="pt-2">
                  <span className="text-[11px] text-zinc-400 block mb-1">
                    Optional / Missing from Posting:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {job.missing_keywords.map((k, i) => (
                      <span
                        key={i}
                        className="rounded-md border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-300"
                      >
                        ! {k}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* CV Suggestions */}
          {job.cv_suggestions && job.cv_suggestions.length > 0 && (
            <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-2 flex items-center gap-2">
                <FileText className="h-3.5 w-3.5 text-indigo-400" />
                <span>Tailored CV Tips</span>
              </h4>
              <ul className="space-y-1.5">
                {job.cv_suggestions.map((tip, i) => (
                  <li key={i} className="text-xs text-zinc-300 leading-relaxed flex items-start gap-2">
                    <span className="text-indigo-400 mt-0.5">🎯</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Referral Kit — as buttons, not a wall of text */}
          <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
            <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-3 flex items-center gap-2">
              <Users className="h-3.5 w-3.5 text-amber-400" />
              <span>Referral Kit — {job.company}</span>
            </h4>
            
            {/* Search Buttons */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-4">
              {referralSearchUrl && (
                <a
                  href={referralSearchUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 rounded-xl border border-sky-500/30 bg-sky-500/10 hover:bg-sky-500/20 px-3 py-2.5 text-xs font-semibold text-sky-300 transition-colors"
                >
                  <Users className="h-3.5 w-3.5" />
                  Engineers
                </a>
              )}
              {recruiterSearchUrl && (
                <a
                  href={recruiterSearchUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 rounded-xl border border-purple-500/30 bg-purple-500/10 hover:bg-purple-500/20 px-3 py-2.5 text-xs font-semibold text-purple-300 transition-colors"
                >
                  <UserCheck className="h-3.5 w-3.5" />
                  Recruiters
                </a>
              )}
              {managerSearchUrl && (
                <a
                  href={managerSearchUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 px-3 py-2.5 text-xs font-semibold text-amber-300 transition-colors"
                >
                  <Building2 className="h-3.5 w-3.5" />
                  Managers
                </a>
              )}
            </div>

            {/* Connection Note (copyable) */}
            <div className="mb-3">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] text-zinc-400 font-medium">Connection Note</span>
                <button
                  onClick={handleCopyNote}
                  className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300"
                >
                  {copiedNote ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedNote ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <div className="font-mono text-xs text-zinc-300 bg-[#0c0d16] p-3 rounded-xl border border-[#1b1c2b]">
                {connectionNote}
              </div>
            </div>

            {/* Referral Message (copyable) */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-[11px] text-zinc-400 font-medium">Referral Request Message</span>
                <button
                  onClick={handleCopyMsg}
                  className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300"
                >
                  {copiedMsg ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  <span>{copiedMsg ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <div className="font-mono text-xs text-zinc-300 bg-[#0c0d16] p-3 rounded-xl border border-[#1b1c2b] whitespace-pre-line leading-relaxed">
                {referralMessage}
              </div>
            </div>
          </div>

          {/* Safety note */}
          <div className="text-[11px] text-zinc-500 italic">
            * Guardrails Active: Claude Sonnet does not hallucinate false experience or unearned credentials. All tailored points are verified against your master CV.
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-[#212439] bg-[#131525] p-5">
          <button
            onClick={onClose}
            className="rounded-xl border border-[#272a42] bg-[#181a2c] hover:bg-[#20233b] px-4 py-2 text-xs font-semibold text-zinc-300 transition-colors"
          >
            Close
          </button>

          <div className="flex items-center gap-2">
            {referralSearchUrl && (
              <a
                href={referralSearchUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 px-4 py-2 text-xs font-bold text-amber-300 transition-all"
              >
                <Users className="h-3.5 w-3.5" />
                <span>Find Referral</span>
              </a>
            )}
            <a
              href={job.url}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 px-5 py-2 text-xs font-bold text-white shadow-lg shadow-indigo-600/30 transition-all"
            >
              <span>Apply Now</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
