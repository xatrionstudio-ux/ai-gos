import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Growth Operating System',
  description: 'Autonomous platform operating the entire marketing & knowledge lifecycle of multiple SaaS products.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-slate-100 antialiased">
        {children}
      </body>
    </html>
  );
}
