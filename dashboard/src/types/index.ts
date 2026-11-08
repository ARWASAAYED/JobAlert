export type WorkType = 'Remote' | 'Hybrid' | 'On-site' | 'Remote / Hybrid' | 'Hybrid / On-site' | string;

export interface Job {
  id: string;
  source: 'linkedin' | 'indeed' | 'remoteok' | 'wwr' | 'wuzzuf' | 'remotive' | 'freehire' | 'jobicy' | string;
  title: string;
  company: string;
  location: string;
  url: string;
  posted_text: string;
  posted_at?: string;
  description: string;
  remote: boolean;
  work_type: WorkType;
  country: string;
  applicants?: string;
  matched_at?: string;
  match_score?: number;
  verdict?: string;
  matched_keywords?: string[];
  missing_keywords?: string[];
  cv_suggestions?: string[];
  cv_generated?: boolean;
}

export interface BotStats {
  jobs_found_today: number;
  jobs_found_week: number;
  alerts_sent: number;
  sources_active: number;
  sources_total: number;
  last_poll: string | null;
  bot_username: string;
  is_online: boolean;
}

export interface BotConfig {
  telegram_token: string;
  telegram_chat_id: string;
  cron_secret: string;
  anthropic_api_key?: string;
  smtp_user?: string;
  sources: {
    linkedin: boolean;
    indeed: boolean;
    remoteok: boolean;
    wwr: boolean;
    wuzzuf: boolean;
    remotive: boolean;
    freehire: boolean;
    jobicy: boolean;
  };
  filters: {
    title_must: string[];
    title_exclude: string[];
    max_years: number;
    locations: string[];
  };
  poll_interval: number;
  max_age_minutes: number;
}

export interface Activity {
  id: string;
  type: 'job_found' | 'alert_sent' | 'cv_generated' | 'error' | 'poll';
  message: string;
  timestamp: string;
  source?: string;
}

export interface TelegramBotInfo {
  id: number;
  is_bot: boolean;
  first_name: string;
  username: string;
  can_join_groups: boolean;
}
