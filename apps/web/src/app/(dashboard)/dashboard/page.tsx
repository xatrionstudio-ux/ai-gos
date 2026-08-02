'use client';

import {
  Activity,
  ArrowUpRight,
  Brain,
  CheckCircle2,
  Clock,
  DollarSign,
  FileText,
  Layers,
  Play,
  Sparkles,
  TrendingUp,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const stats = [
    { name: 'Active Workflows', value: '4 Running', sub: '2 waiting approval', icon: Activity, color: 'text-brand' },
    { name: 'Product Knowledge Chunks', value: '14,280', sub: 'Single Source of Truth', icon: Brain, color: 'text-accent-emerald' },
    { name: 'Published Content (30d)', value: '184 Articles', sub: '+34% vs last month', icon: FileText, color: 'text-blue-400' },
    { name: 'AI Operating Cost', value: '$42.18', sub: 'Avg $0.23 / article', icon: DollarSign, color: 'text-accent-amber' },
  ];

  const activeWorkflows = [
    {
      id: 'wf-1049',
      name: 'SEO Pillar Strategy — Hypnotherapy SaaS',
      project: 'TranceOS',
      currentStep: 'BrandReviewerAgent',
      confidence: 0.96,
      status: 'running',
      timeElapsed: '4m 12s',
    },
    {
      id: 'wf-1048',
      name: 'Product Update Cascade — Git Commit 4a8e2f',
      project: 'Moneyly',
      currentStep: 'HumanApprovalNode',
      confidence: 0.99,
      status: 'waiting_approval',
      timeElapsed: '12m 45s',
    },
    {
      id: 'wf-1045',
      name: 'Content Decay Refresh — GA4 Traffic Alert',
      project: 'ConstruAI',
      currentStep: 'FactCheckerAgent',
      confidence: 0.94,
      status: 'running',
      timeElapsed: '1m 08s',
    },
  ];

  const pendingApprovals = [
    {
      id: 'app-901',
      title: 'Outline Review: "Complete Guide to HIPAA Compliant Telehealth in 2026"',
      type: 'Outline Approval',
      project: 'TranceOS',
      requested: '10m ago',
    },
    {
      id: 'app-900',
      title: 'Publication Review: "How Moneyly Automates Payroll Tax Deductions"',
      type: 'Final Publish Approval',
      project: 'Moneyly',
      requested: '35m ago',
    },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-white">Autonomous Control Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time status of 26 specialized AI agents running LangGraph workflows across SaaS products.
          </p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/workflows/new"
            className="px-4 py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-brand/20 transition-all"
          >
            <Play className="w-4 h-4" />
            <span>Launch Workflow</span>
          </Link>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => {
          const Icon = s.icon;
          return (
            <div key={s.name} className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-slate-400">{s.name}</span>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <div>
                <p className="text-2xl font-bold text-white font-mono">{s.value}</p>
                <p className="text-xs text-slate-500 mt-1">{s.sub}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Signature Element — Active LangGraph Workflow Visualizer */}
      <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-6">
        <div className="flex items-center justify-between border-b border-surface-border pb-4">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 rounded-full bg-accent-emerald animate-pulse" />
            <h2 className="font-display font-semibold text-lg text-white">
              Live LangGraph Workflow Engine — Monitored Pipeline
            </h2>
          </div>
          <span className="text-xs font-mono text-slate-400">Thread #wf-1049 • High Confidence</span>
        </div>

        {/* Node Pipeline Diagram */}
        <div className="py-6 px-4 bg-background rounded-lg border border-surface-border overflow-x-auto">
          <div className="flex items-center justify-between min-w-[750px] relative">
            {/* Step 1 */}
            <div className="flex flex-col items-center gap-2 z-10">
              <div className="w-10 h-10 rounded-lg bg-surface border border-accent-emerald flex items-center justify-center text-accent-emerald font-mono text-xs font-bold">
                ✓
              </div>
              <span className="text-xs font-mono text-slate-300">SERP Research</span>
              <span className="text-[10px] text-slate-500">100% conf</span>
            </div>

            <div className="flex-1 h-0.5 bg-accent-emerald mx-2" />

            {/* Step 2 */}
            <div className="flex flex-col items-center gap-2 z-10">
              <div className="w-10 h-10 rounded-lg bg-surface border border-accent-emerald flex items-center justify-center text-accent-emerald font-mono text-xs font-bold">
                ✓
              </div>
              <span className="text-xs font-mono text-slate-300">Outline Generator</span>
              <span className="text-[10px] text-slate-500">Approved</span>
            </div>

            <div className="flex-1 h-0.5 bg-accent-emerald mx-2" />

            {/* Step 3 */}
            <div className="flex flex-col items-center gap-2 z-10">
              <div className="w-10 h-10 rounded-lg bg-surface border border-accent-emerald flex items-center justify-center text-accent-emerald font-mono text-xs font-bold">
                ✓
              </div>
              <span className="text-xs font-mono text-slate-300">Writer Agent</span>
              <span className="text-[10px] text-slate-500">2,450 words</span>
            </div>

            <div className="flex-1 h-0.5 bg-brand mx-2 animate-pulse" />

            {/* Active Step */}
            <div className="flex flex-col items-center gap-2 z-10">
              <div className="w-12 h-12 rounded-lg bg-brand border-2 border-brand/50 flex items-center justify-center text-white font-mono text-xs font-bold agent-node-active">
                <Sparkles className="w-5 h-5 animate-spin" />
              </div>
              <span className="text-xs font-mono font-semibold text-brand">Brand Reviewer</span>
              <span className="text-[10px] text-slate-400 font-mono">Evaluating Tone...</span>
            </div>

            <div className="flex-1 h-0.5 bg-surface-border mx-2" />

            {/* Step 5 */}
            <div className="flex flex-col items-center gap-2 z-10 opacity-50">
              <div className="w-10 h-10 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-slate-500 font-mono text-xs">
                5
              </div>
              <span className="text-xs font-mono text-slate-500">Fact Checker</span>
              <span className="text-[10px] text-slate-600">Pending</span>
            </div>

            <div className="flex-1 h-0.5 bg-surface-border mx-2" />

            {/* Step 6 */}
            <div className="flex flex-col items-center gap-2 z-10 opacity-50">
              <div className="w-10 h-10 rounded-lg bg-surface border border-surface-border flex items-center justify-center text-slate-500 font-mono text-xs">
                6
              </div>
              <span className="text-xs font-mono text-slate-500">Publisher</span>
              <span className="text-[10px] text-slate-600">Pending</span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid: Active Workflows & Approvals */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Workflows List (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-semibold text-base text-white">Active Workflows</h3>
            <Link href="/workflows" className="text-xs text-brand hover:underline flex items-center gap-1">
              View All <ArrowUpRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="space-y-3">
            {activeWorkflows.map((wf) => (
              <div
                key={wf.id}
                className="p-4 rounded-lg bg-background border border-surface-border hover:border-surface-hover transition-all flex items-center justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-brand/10 text-brand border border-brand/20">
                      {wf.project}
                    </span>
                    <span className="text-sm font-medium text-white">{wf.name}</span>
                  </div>
                  <p className="text-xs text-slate-400 font-mono">
                    Current Agent: <span className="text-slate-200">{wf.currentStep}</span> • Confidence: {(wf.confidence * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="flex items-center gap-4">
                  {wf.status === 'waiting_approval' ? (
                    <span className="px-2.5 py-1 rounded text-xs font-semibold bg-accent-amber/20 text-accent-amber border border-accent-amber/30 flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      Approval Needed
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded text-xs font-semibold bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 animate-spin" />
                      Processing
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Human In The Loop Approval Queue (1 col) */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-semibold text-base text-white">Approval Queue</h3>
            <span className="px-2 py-0.5 text-xs font-mono rounded-full bg-accent-amber/20 text-accent-amber border border-accent-amber/30">
              2 Pending
            </span>
          </div>

          <div className="space-y-3">
            {pendingApprovals.map((app) => (
              <div key={app.id} className="p-4 rounded-lg bg-background border border-surface-border space-y-3">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-mono text-brand">{app.project}</span>
                  <span>{app.requested}</span>
                </div>
                <p className="text-sm font-medium text-slate-200 line-clamp-2">{app.title}</p>
                <div className="flex gap-2 pt-1">
                  <Link
                    href={`/approvals/${app.id}`}
                    className="flex-1 py-1.5 text-center text-xs font-semibold rounded bg-brand text-white hover:bg-brand-hover transition-colors"
                  >
                    Review & Edit
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
