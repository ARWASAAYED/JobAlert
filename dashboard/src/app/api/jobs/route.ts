import { NextResponse } from 'next/server';
import { INITIAL_JOBS } from '@/lib/mock-data';

export const dynamic = 'force-dynamic';

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
        return NextResponse.json({
          jobs: data.jobs,
          total: data.jobs.length,
          source: 'redis_live',
        });
      }
    }
  } catch (err) {
    console.warn('Live feed fetch error, falling back to mock jobs:', err);
  }

  return NextResponse.json({
    jobs: INITIAL_JOBS,
    total: INITIAL_JOBS.length,
    source: 'mock_fallback',
  });
}


