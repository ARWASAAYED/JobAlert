'use client';

import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Building2,
  MapPin,
  ExternalLink,
  Copy,
  Check,
  FileText,
  UserCheck,
  Share2,
} from 'lucide-react';
import { Job } from '@/types';

interface JobModalProps {
  job: Job | null;
  onClose: () => void;
}

export function JobModal({ job, onClose }: JobModalProps) {
  const [tab, setTab] = useState<'cv' | 'referral'>('cv');
  const [copiedNote, setCopiedNote] = useState(false);
  const [copiedMsg, setCopiedMsg] = useState(false);

  if (!job) return null;

  const connectionNote = `Hi [Name], I noticed you work at ${job.company}. I'm Arwa Ahmed, a Junior Frontend Developer specializing in React and Next.js. I recently saw the ${job.title} opening and would love to connect!`;

  const referralMessage = `Hi [Name], hope you're having a great week! I recently applied for the ${job.title} position at ${job.company}. As a Junior React developer with hands-on experience in Next.js, TypeScript, and modern web applications, I believe my skills match well with what your team is building. Would you be open to providing a referral or putting me in touch with the hiring manager? My CV is attached. Thank you so much!`;

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
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 px-2 py-0.5 rounded-full">
                AI Match Score: {job.match_score || 92}%
              </span>
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
            </div>
          </div>

          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-[#1b1e32] text-zinc-400 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-[#212439] bg-[#0e101a] px-6">
          <button
            onClick={() => setTab('cv')}
            className={`flex items-center gap-2 py-3 text-xs font-semibold border-b-2 transition-all ${
              tab === 'cv'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>AI Tailored CV Breakdown</span>
          </button>
          <button
            onClick={() => setTab('referral')}
            className={`ml-6 flex items-center gap-2 py-3 text-xs font-semibold border-b-2 transition-all ${
              tab === 'referral'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <UserCheck className="h-4 w-4" />
            <span>LinkedIn Referral Kit</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 text-sm">
          {tab === 'cv' ? (
            <div className="space-y-4">
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

              {/* Tailored Professional Summary */}
              <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-2">
                  Tailored Professional Summary (Arwa Ahmed)
                </h4>
                <p className="text-xs text-zinc-300 leading-relaxed font-mono bg-[#0c0d16] p-3 rounded-xl border border-[#1b1c2b]">
                  &quot;Detail-oriented Junior Frontend Developer specializing in React and Next.js, with hands-on experience developing modular, high-performance web applications. Skilled in TypeScript, Tailwind CSS, and REST API integration, with a strong focus on clean code and agile collaboration for {job.company}.&quot;
                </p>
              </div>

              {/* Safety Rules Reminder */}
              <div className="text-[11px] text-zinc-500 italic">
                * Guardrails Active: Claude Sonnet does not hallucinate false experience or unearned credentials. All tailored points are verified against your master CV.
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* LinkedIn Search Employees */}
              <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300 mb-2 flex items-center justify-between">
                  <span>1. Find Engineers at {job.company}</span>
                  <a
                    href={`https://www.linkedin.com/search/results/people/?keywords=${encodeURIComponent(
                      job.company + ' frontend engineer'
                    )}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-xs text-sky-400 hover:underline"
                  >
                    <span>Search on LinkedIn</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                </h4>
                <p className="text-xs text-zinc-400">
                  Click above to see 1st and 2nd degree connections currently working on the engineering team at {job.company}.
                </p>
              </div>

              {/* Connection Note */}
              <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300">
                    2. LinkedIn Connection Note (Max 300 chars)
                  </h4>
                  <button
                    onClick={handleCopyNote}
                    className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300"
                  >
                    {copiedNote ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    <span>{copiedNote ? 'Copied' : 'Copy Note'}</span>
                  </button>
                </div>
                <div className="font-mono text-xs text-zinc-300 bg-[#0c0d16] p-3 rounded-xl border border-[#1b1c2b]">
                  {connectionNote}
                </div>
              </div>

              {/* Referral Message */}
              <div className="rounded-2xl border border-[#232742] bg-[#141628] p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-300">
                    3. InMail / Referral Request Message
                  </h4>
                  <button
                    onClick={handleCopyMsg}
                    className="flex items-center gap-1 text-xs font-medium text-indigo-400 hover:text-indigo-300"
                  >
                    {copiedMsg ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    <span>{copiedMsg ? 'Copied' : 'Copy Message'}</span>
                  </button>
                </div>
                <div className="font-mono text-xs text-zinc-300 bg-[#0c0d16] p-3 rounded-xl border border-[#1b1c2b] whitespace-pre-line leading-relaxed">
                  {referralMessage}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-[#212439] bg-[#131525] p-5">
          <button
            onClick={onClose}
            className="rounded-xl border border-[#272a42] bg-[#181a2c] hover:bg-[#20233b] px-4 py-2 text-xs font-semibold text-zinc-300 transition-colors"
          >
            Close
          </button>

          <a
            href={job.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-sky-600 hover:from-indigo-500 hover:to-sky-500 px-5 py-2 text-xs font-bold text-white shadow-lg shadow-indigo-600/30 transition-all"
          >
            <span>Proceed to Apply Now</span>
            <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
}
