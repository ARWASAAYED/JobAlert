import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function timeAgo(dateString: string): string {
  try {
    const now = new Date();
    const date = new Date(dateString);
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSeconds < 60) return 'just now';
    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  } catch {
    return dateString;
  }
}

export function sourceBadgeColor(source: string): { bg: string; text: string; border: string; dot: string } {
  switch (source.toLowerCase()) {
    case 'linkedin':
      return {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500/30',
        dot: 'bg-blue-500',
      };
    case 'indeed':
      return {
        bg: 'bg-indigo-500/10',
        text: 'text-indigo-400',
        border: 'border-indigo-500/30',
        dot: 'bg-indigo-500',
      };
    case 'remoteok':
      return {
        bg: 'bg-emerald-500/10',
        text: 'text-emerald-400',
        border: 'border-emerald-500/30',
        dot: 'bg-emerald-500',
      };
    case 'wwr':
    case 'weworkremotely':
      return {
        bg: 'bg-amber-500/10',
        text: 'text-amber-400',
        border: 'border-amber-500/30',
        dot: 'bg-amber-500',
      };
    case 'wuzzuf':
      return {
        bg: 'bg-orange-500/10',
        text: 'text-orange-400',
        border: 'border-orange-500/30',
        dot: 'bg-orange-500',
      };
    case 'remotive':
      return {
        bg: 'bg-purple-500/10',
        text: 'text-purple-400',
        border: 'border-purple-500/30',
        dot: 'bg-purple-500',
      };
    case 'freehire':
      return {
        bg: 'bg-cyan-500/10',
        text: 'text-cyan-400',
        border: 'border-cyan-500/30',
        dot: 'bg-cyan-500',
      };
    case 'jobicy':
      return {
        bg: 'bg-rose-500/10',
        text: 'text-rose-400',
        border: 'border-rose-500/30',
        dot: 'bg-rose-500',
      };
    default:
      return {
        bg: 'bg-zinc-500/10',
        text: 'text-zinc-400',
        border: 'border-zinc-500/30',
        dot: 'bg-zinc-400',
      };
  }
}

export function workTypeBadge(workType: string): { emoji: string; label: string; color: string } {
  const wt = (workType || '').toLowerCase();
  if (wt.includes('remote')) {
    return { emoji: '🏠', label: 'Remote', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30' };
  }
  if (wt.includes('hybrid')) {
    return { emoji: '🔄', label: 'Hybrid', color: 'text-amber-400 bg-amber-500/10 border-amber-500/30' };
  }
  return { emoji: '🏢', label: 'On-site', color: 'text-sky-400 bg-sky-500/10 border-sky-500/30' };
}
