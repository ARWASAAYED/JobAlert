import { NextResponse } from 'next/server';

const DEFAULT_TOKEN = '9219037439:AAHOQk7AuLgqyhOWGXlUXx17vV8W8kDkswU';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const token = searchParams.get('token') || process.env.TELEGRAM_TOKEN || DEFAULT_TOKEN;

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/getMe`, {
      cache: 'no-store',
    });
    const data = await res.json();

    if (data.ok) {
      return NextResponse.json({
        ok: true,
        bot: data.result,
      });
    } else {
      return NextResponse.json(
        { ok: false, error: data.description || 'Failed to authenticate bot' },
        { status: 400 }
      );
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json(
      { ok: false, error: message },
      { status: 500 }
    );
  }
}

