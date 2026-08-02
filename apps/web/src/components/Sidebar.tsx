'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderKanban,
  BrainCircuit,
  Workflow,
  CheckCircle2,
  Cpu,
  History,
  Settings,
  Sparkles,
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Knowledge Graph', href: '/knowledge', icon: BrainCircuit },
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Approvals', href: '/approvals', icon: CheckCircle2, badge: '2' },
  { name: 'AI Cost & Traces', href: '/ai/cost', icon: Cpu },
  { name: 'Event Timeline', href: '/events', icon: History },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-6 border-b border-surface-border flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center text-white shadow-lg shadow-brand/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-display font-bold text-base tracking-wide text-white">AI-GOS</h1>
            <p className="text-xs text-slate-400 font-mono">v1.0.0 • Autonomous</p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand/10 text-brand border border-brand/20'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-hover'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand' : 'text-slate-400'}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="px-2 py-0.5 text-xs font-mono font-semibold rounded-full bg-accent-amber/20 text-accent-amber border border-accent-amber/30">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / Tenant info */}
      <div className="p-4 border-t border-surface-border">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-background border border-surface-border">
          <div className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
          <div className="overflow-hidden">
            <p className="text-xs font-semibold text-slate-200 truncate">Trance OS Workspace</p>
            <p className="text-[10px] text-slate-500 font-mono">Multi-Tenant • Enterprise</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
