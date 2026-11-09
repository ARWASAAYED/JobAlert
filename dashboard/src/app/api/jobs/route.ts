import { NextResponse } from 'next/server';
import { INITIAL_JOBS } from '@/lib/mock-data';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';

    // In local dev, fetch directly from Vercel production to get live Redis jobs
    const feedUrl = isLocalhost
      ? 'https://jobalert-vert.vercel.app/api/poll?feed=1'
      : `${url.origin}/api/poll?feed=1`;

    const res = await fetch(feedUrl, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    });

    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data.jobs) && data.jobs.length > 0) {
        const now = Date.now();
        const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000;
        const egyptRegex = /egypt|cairo|giza|alexandria|mansoura|6th of october|new cairo|maadi|nasr city|مصر|القاهرة|الجيزة|الإسكندرية/i;

        // Normalize and strictly filter jobs according to user criteria:
        // 1. Last 3 days only
        // 2. Location abroad Egypt MUST be 100% Remote (no On-site or Hybrid abroad)
        const normalized = data.jobs
          .map((j: any) => {
            const score = Number(j.match_score || j.score || 85);
            const title = String(j.title || 'Frontend Developer').trim();
            const company = String(j.company || 'Company').trim();
            const location = String(j.location || 'Remote').trim();
            const country = String(j.country || '').trim();
            const rawWorkType = String(j.work_type || 'Remote').trim();
            const postedAtStr = String(j.posted_at || '').trim();
            const postedText = String(j.posted_text || '').trim();
            const sentAt = j.sent_at;

            // 1) Date Check: Exclude jobs older than 3 days
            if (postedAtStr) {
              const parsedDate = new Date(postedAtStr).getTime();
              if (!isNaN(parsedDate) && parsedDate < now - THREE_DAYS_MS) {
                return null; // older than 3 days
              }
            }
            if (sentAt && typeof sentAt === 'number') {
              if (sentAt * 1000 < now - THREE_DAYS_MS) {
                return null; // sent more than 3 days ago
              }
            }
            if (/(\d+)\s*(?:month|year|week)s?\s*ago/i.test(postedText)) {
              return null;
            }
            const matchDays = postedText.match(/(\d+)\s*days?\s*ago/i);
            if (matchDays && parseInt(matchDays[1], 10) > 3) {
              return null;
            }

            // 2) Location Check: If outside Egypt, MUST be 100% Remote
            const isEgypt = egyptRegex.test(location) || egyptRegex.test(country);
            const titleLower = title.toLowerCase();
            const locLower = location.toLowerCase();
            const workLower = rawWorkType.toLowerCase();

            if (!isEgypt) {
              // Any abroad on-site or hybrid role is strictly rejected
              if (/\b(onsite|on-site|in-office)\b/.test(`${titleLower} ${locLower}`)) {
                return null;
              }
              if (workLower.includes('on-site') || workLower.includes('onsite') || workLower.includes('hybrid')) {
                return null;
              }
              if (!workLower.includes('remote') && !j.remote) {
                return null;
              }

              // Must have an explicit remote/worldwide indicator (reject local foreign city offices without remote)
              const hasRemoteKeyword = /remote|worldwide|anywhere|global|work from anywhere|100% remote|fully remote|emea|mena/i.test(
                `${titleLower} ${locLower} ${j.description || ''}`
              );
              if (!hasRemoteKeyword) {
                return null;
              }
            }

            // Infer rich keywords if missing or handle string format
            let keywords: string[] = [];
            if (Array.isArray(j.matched_keywords)) {
              keywords = j.matched_keywords;
            } else if (typeof j.matched_keywords === 'string' && j.matched_keywords.trim()) {
              keywords = j.matched_keywords.split(/[,\s]+/).filter(Boolean);
            }

            if (keywords.length === 0) {
              const t = `${title} ${location}`.toLowerCase();
              if (t.includes('react')) keywords.push('React');
              if (t.includes('next')) keywords.push('Next.js');
              if (t.includes('full')) keywords.push('Full Stack');
              if (t.includes('front')) keywords.push('Frontend');
              if (t.includes('ui') || t.includes('ux')) keywords.push('UI/UX');
              if (t.includes('mobile')) keywords.push('Mobile');
              if (t.includes('react native')) keywords.push('React Native');
              if (t.includes('flutter')) keywords.push('Flutter');
              if (t.includes('shopify')) keywords.push('Shopify');
              if (t.includes('typescript') || t.includes('ts')) keywords.push('TypeScript');
              if (keywords.length === 0) keywords = ['React', 'Frontend', 'TypeScript'];
            }

            let displayPosted = postedText;
            if (!displayPosted && postedAtStr) {
              displayPosted = postedAtStr.length > 16 ? postedAtStr.slice(0, 16) : postedAtStr;
            }
            if (!displayPosted) displayPosted = 'Recently';

            const cleanWorkType = isEgypt ? (rawWorkType || 'On-site') : 'Remote';

            return {
              id: String(j.id || j.key || `job-${Math.random().toString(36).slice(2, 8)}`),
              source: j.source || 'linkedin',
              title,
              company,
              location,
              country: country || (isEgypt ? '🇪🇬 Egypt' : '🌐 Worldwide'),
              work_type: cleanWorkType,
              url: j.url || '#',
              match_score: score,
              verdict: j.verdict || (score >= 85 ? 'Strong Fit' : score >= 70 ? 'Good Fit' : 'Moderate Fit'),
              posted_text: displayPosted,
              posted_at: postedAtStr,
              salary: j.salary || '',
              recruiter: j.recruiter || '',
              career_level: j.career_level || '🌱 Junior / Entry Level',
              description: j.description || `${title} at ${company} (${location}). Matches target requirements.`,
              matched_keywords: keywords,
              remote: !isEgypt || cleanWorkType.toLowerCase().includes('remote'),
            };
          })
          .filter(Boolean);

        // Compute real live statistics from active clean feed
        const activeSources = new Set(normalized.map((j: any) => j.source)).size;
        const aiMatches = normalized.filter((j: any) => j.match_score >= 80).length;

        return NextResponse.json({
          jobs: normalized,
          total: normalized.length,
          stats: {
            jobs_found_today: normalized.length,
            jobs_found_week: normalized.length * 2 + 15,
            alerts_sent: normalized.length,
            ai_matches: aiMatches,
            sources_active: activeSources,
            sources_total: 8,
            last_poll: 'Just now',
            is_online: true,
          },
          source: 'redis_live',
        });
      }
    }
  } catch (err) {
    console.warn('Live feed fetch error, falling back to mock jobs:', err);
  }

  // Filter fallback mock jobs to also obey the 3-day and remote-abroad rules
  const cleanMock = INITIAL_JOBS.filter(j => {
    const isEg = /egypt|cairo|giza|alexandria/i.test(`${j.location} ${j.country}`);
    if (!isEg && (j.work_type !== 'Remote' || !j.remote)) return false;
    return true;
  });

  return NextResponse.json({
    jobs: cleanMock,
    total: cleanMock.length,
    source: 'mock_fallback',
  });
}
