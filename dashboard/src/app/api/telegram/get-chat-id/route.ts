import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const token = searchParams.get('token') || process.env.TELEGRAM_TOKEN;
  if (!token || token.includes('•')) {
    return NextResponse.json({
      ok: false,
      hint: 'Bot token is protected in server environment (.env).',
    });
  }

  try {
    const res = await fetch(`https://api.telegram.org/bot${token}/getUpdates`, {
      cache: 'no-store',
    });
    const data = await res.json();

    if (!data.ok) {
      return NextResponse.json(
        { ok: false, error: data.description || 'Failed to fetch updates' },
        { status: 400 }
      );
    }

    const updates = data.result || [];
    const chats: { id: number; name: string; username?: string; text?: string; date: number }[] = [];

    for (const u of [...updates].reverse()) {
      const msg = u.message || u.channel_post;
      if (msg && msg.chat) {
        const id = msg.chat.id;
        if (!chats.some((c) => c.id === id)) {
          chats.push({
            id,
            name: `${msg.chat.first_name || ''} ${msg.chat.last_name || ''}`.trim() || msg.chat.title || 'Unknown',
            username: msg.chat.username,
            text: msg.text,
            date: msg.date,
          });
        }
      }
    }

    return NextResponse.json({
      ok: true,
      chats,
      count: chats.length,
      latest_chat_id: chats.length > 0 ? chats[0].id : null,
      hint: chats.length === 0 ? 'No messages received yet. Please open Telegram, search @MyFuckingJobAlertbot and send /start' : null,
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error';
    return NextResponse.json(
      { ok: false, error: message },
      { status: 500 }
    );
  }
}

