import { NextResponse } from 'next/server';

const DEFAULT_TOKEN = '9219037439:AAHOQk7AuLgqyhOWGXlUXx17vV8W8kDkswU';

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const token = body.token || process.env.TELEGRAM_TOKEN || DEFAULT_TOKEN;
    const chatId = body.chat_id || process.env.TELEGRAM_CHAT_ID;

    if (!chatId) {
      return NextResponse.json(
        {
          ok: false,
          error: 'Missing Chat ID. Please send /start to @MyFuckingJobAlertbot and detect your Chat ID first.',
        },
        { status: 400 }
      );
    }

    const message = `🚨 <b>Junior React Developer</b>\n🏢 Vodafone Intelligent Solutions (_VOIS)\n📍 Cairo, Egypt  ·  💼 Hybrid\n⏱ Just now\n🌐 LinkedIn\n\n🎯 <b>Match Score: 95%</b>\n✅ Skills: React, Next.js, TypeScript, Tailwind CSS\n\n<i>This is a test notification from your JobAlert Dashboard!</i>`;

    const res = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'HTML',
        disable_web_page_preview: true,
        reply_markup: {
          inline_keyboard: [
            [
              {
                text: '⚡ قدّمي دلوقتي (Apply Now)',
                url: 'https://linkedin.com',
              },
            ],
            [
              {
                text: '📊 Open Dashboard',
                url: 'https://vercel.com',
              },
            ],
          ],
        },
      }),
    });

    const data = await res.json();
    if (data.ok) {
      return NextResponse.json({
        ok: true,
        message: 'Test alert sent successfully to Telegram!',
        result: data.result,
      });
    } else {
      return NextResponse.json(
        { ok: false, error: data.description || 'Telegram API returned an error' },
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
