import { NextResponse } from 'next/server';
import { INITIAL_CONFIG } from '@/lib/mock-data';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';
    const targetUrl = isLocalhost
      ? 'https://jobalert-vert.vercel.app/api/poll?config=1'
      : `${url.origin}/api/poll?config=1`;

    const res = await fetch(targetUrl, {
      cache: 'no-store',
      headers: { Accept: 'application/json' },
    });

    if (res.ok) {
      const data = await res.json();
      if (data.config) {
        return NextResponse.json({ config: data.config, source: 'redis' });
      }
    }
  } catch (err) {
    console.warn('Failed to fetch remote config:', err);
  }

  return NextResponse.json({ config: INITIAL_CONFIG, source: 'default' });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const url = new URL(req.url);
    const isLocalhost = url.hostname === 'localhost' || url.hostname === '127.0.0.1';
    const targetUrl = isLocalhost
      ? 'https://jobalert-vert.vercel.app/api/poll'
      : `${url.origin}/api/poll`;

    const res = await fetch(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (res.ok) {
      return NextResponse.json({ ok: true, saved: body });
    }
    return NextResponse.json({ ok: false, error: 'Remote save failed' }, { status: 500 });
  } catch (err: any) {
    return NextResponse.json({ ok: false, error: err.message }, { status: 500 });
  }
}

