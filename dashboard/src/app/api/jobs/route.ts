import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import { INITIAL_JOBS } from '@/lib/mock-data';

export async function GET() {
  try {
    const jsonPath = path.join(process.cwd(), 'public', 'jobs.json');
    if (fs.existsSync(jsonPath)) {
      const data = fs.readFileSync(jsonPath, 'utf-8');
      const jobs = JSON.parse(data);
      if (Array.isArray(jobs) && jobs.length > 0) {
        return NextResponse.json({ jobs, total: jobs.length });
      }
    }
  } catch (err) {
    console.error('Failed reading public/jobs.json:', err);
  }

  return NextResponse.json({ jobs: INITIAL_JOBS, total: INITIAL_JOBS.length });
}

