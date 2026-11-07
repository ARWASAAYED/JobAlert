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

    const now = new Date();
    const formattedDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    const testJobId = '4485506218';
    const testJobUrl = `https://www.linkedin.com/jobs/view/${testJobId}/`;
    const testLiUrl = `https://linkedin.com/jobs/view/${testJobId}`;

    const message = [
      '🇪🇬 🆕 Shopify developer',
      '🏢 Republic- Job Company',
      `🕐 Posted ${formattedDate}`,
      `<a href="${testJobUrl}">View</a>`,
      `<a href="${testLiUrl}">Linkedin</a>`,
      'Shopify developer at Republic- Job Company — Cairo, Egypt |',
    ].join('\n');

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
                text: '⚡ View Job',
                url: testJobUrl,
              },
              {
                text: '🔗 LinkedIn',
                url: testLiUrl,
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

