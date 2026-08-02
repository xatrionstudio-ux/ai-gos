'use client';

import { useState } from 'react';
import {
  Workflow,
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Terminal,
  ChevronRight,
} from 'lucide-react';

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState('wf-1049');

  const workflows = [
    {
      id: 'wf-1049',
      type: 'SEO Content Workflow',
      project: 'TranceOS',
      status: 'running',
      node: 'BrandReviewerAgent',
      startTime: '2026-08-02 04:45:10',
      duration: '4m 12s',
      logs: [
        '[04:45:10] Workflow initiated for keyword: "HIPAA Compliant Telehealth Platform"',
        '[04:45:12] SERPResearcherAgent fetched 10 Google SERP results.',
        '[04:45:18] CompetitorResearcherAgent analyzed top 3 ranking URLs.',
        '[04:45:25] EvidenceCollectorAgent extracted 14 evidence items from Product Knowledge Layer.',
        '[04:45:32] OutlineGeneratorAgent generated H1-H4 brief (12 sections).',
        '[04:45:45] Outline auto-approved based on 0.98 confidence threshold.',
        '[04:46:12] WriterAgent generated 2,450-word draft using Claude-3.5-Sonnet.',
        '[04:46:50] SEOOptimizerAgent applied JSON-LD schema & internal links.',
        '[04:47:15] BrandReviewerAgent evaluating tone against TranceOS style guide...',
      ],
    },
    {
      id: 'wf-1048',
      type: 'Product Update Workflow',
      project: 'Moneyly',
      status: 'waiting_approval',
      node: 'HumanApprovalNode',
      startTime: '2026-08-02 04:32:00',
      duration: '12m 45s',
      logs: [
        '[04:32:00] Webhook received: Git Commit 4a8e2f (feature: Automated Payroll Tax)',
        '[04:32:05] KnowledgeBuilderAgent updated Product Knowledge Graph (+3 entities).',
        '[04:32:20] DocumentationUpdater generated draft docs page.',
        '[04:32:40] NewsletterAgent generated email campaign brief.',
        '[04:33:00] Checkpoint paused: Awaiting Human Approval before publishing to WordPress CMS.',
      ],
    },
  ];

  const activeWf = workflows.find((w) => w.id === selectedWorkflow) || workflows[0];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-white">LangGraph Workflow Monitor</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time execution status, SSE streaming logs, checkpoint state, and controls.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Workflow List (1 col) */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <h3 className="font-display font-semibold text-base text-white">Execution Threads</h3>
          <div className="space-y-3">
            {workflows.map((w) => (
              <button
                key={w.id}
                onClick={() => setSelectedWorkflow(w.id)}
                className={`w-full text-left p-4 rounded-lg border transition-all space-y-2 ${
                  selectedWorkflow === w.id
                    ? 'bg-brand/10 border-brand/40 text-white'
                    : 'bg-background border-surface-border text-slate-300 hover:bg-surface-hover'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-brand font-semibold">{w.project}</span>
                  <span className="font-mono text-slate-500">{w.id}</span>
                </div>
                <p className="text-sm font-medium">{w.type}</p>
                <div className="flex items-center justify-between text-xs pt-1 text-slate-400">
                  <span>Step: {w.node}</span>
                  <span className="font-mono">{w.duration}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Real-Time Log Terminal & Controls (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-surface border border-surface-border space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            {/* Control Bar */}
            <div className="flex items-center justify-between border-b border-surface-border pb-4">
              <div>
                <span className="text-xs font-mono text-slate-400">{activeWf.project} / {activeWf.id}</span>
                <h2 className="font-display font-semibold text-lg text-white">{activeWf.type}</h2>
              </div>
              <div className="flex gap-2">
                <button className="px-3 py-1.5 rounded text-xs font-semibold bg-surface-border hover:bg-surface-hover text-slate-200 flex items-center gap-1.5 transition-colors">
                  <Pause className="w-3.5 h-3.5" /> Pause
                </button>
                <button className="px-3 py-1.5 rounded text-xs font-semibold bg-surface-border hover:bg-surface-hover text-slate-200 flex items-center gap-1.5 transition-colors">
                  <RotateCcw className="w-3.5 h-3.5" /> Rollback
                </button>
                <button className="px-3 py-1.5 rounded text-xs font-semibold bg-brand text-white hover:bg-brand-hover flex items-center gap-1.5 transition-colors">
                  <Play className="w-3.5 h-3.5" /> Resume
                </button>
              </div>
            </div>

            {/* Terminal View */}
            <div className="p-4 rounded-lg bg-black border border-surface-border font-mono text-xs text-slate-300 space-y-2 h-96 overflow-y-auto">
              <div className="flex items-center gap-2 text-slate-500 border-b border-slate-800 pb-2 mb-3">
                <Terminal className="w-4 h-4 text-brand" />
                <span>Streaming Logs (SSE connected)</span>
              </div>
              {activeWf.logs.map((log, idx) => (
                <div key={idx} className="leading-relaxed font-mono">
                  <span className="text-slate-500">{log.substring(0, 10)}</span>
                  <span className="text-slate-200">{log.substring(10)}</span>
                </div>
              ))}
              {activeWf.status === 'running' && (
                <div className="flex items-center gap-2 text-brand pt-2">
                  <Activity className="w-3.5 h-3.5 animate-spin" />
                  <span>Agent process executing...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
