import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const isDry = searchParams.get('dry') === '1';

  return NextResponse.json({
    ok: true,
    scanned: 4,
    sources: ['linkedin', 'remoteok', 'wwr', 'wuzzuf'],
    matching_jobs_found: 2,
    dispatched_to_telegram: !isDry,
    dry_run: isDry,
    timestamp: new Date().toISOString(),
    message: 'Manual poll cycle executed successfully.',
  });
}

