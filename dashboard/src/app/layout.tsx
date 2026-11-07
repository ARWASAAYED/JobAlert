import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'JobAlert — AI Job Hunting & Telegram Bot Dashboard',
  description: 'Real-time job scraper and AI-powered CV tailoring bot for Junior React & Frontend Developers in Egypt and Worldwide.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#090a10] text-zinc-100 antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
