'use client';

import { useState } from 'react';
import { CheckCircle2, XCircle, Edit3, Sparkles, ShieldCheck, FileText, ArrowRight } from 'lucide-react';

export default function ApprovalsPage() {
  const [selectedApproval, setSelectedApproval] = useState('app-901');

  const approvals = [
    {
      id: 'app-901',
      title: 'Outline Review: "Complete Guide to HIPAA Compliant Telehealth in 2026"',
      type: 'Outline Approval',
      project: 'TranceOS',
      requestedBy: 'OutlineGeneratorAgent',
      confidence: 0.98,
      status: 'pending',
      summary: '12 sections covering HIPAA Security Rule, video encryption, audit logs, and BAA requirements.',
      contentPreview: `
# Complete Guide to HIPAA Compliant Telehealth in 2026

## 1. Introduction: The Modern Telehealth Compliance Landscape
- Key updates to HIPAA Security Rule in 2026
- Why generic video tools fail compliance audits

## 2. Technical Requirements for HIPAA Video Servers
- WebRTC end-to-end encryption standards
- Dedicated private TURN/STUN servers
- Zero-retention recording policies

## 3. Business Associate Agreements (BAA) Explained
- Required contractual clauses for SaaS vendors
- How TranceOS signs automated BAAs

## 4. Audit Logging & Access Controls
- Role-Based Access Control (RBAC) for session logs
- Automated session termination after 15m inactivity
      `,
    },
    {
      id: 'app-900',
      title: 'Publication Review: "How Moneyly Automates Payroll Tax Deductions"',
      type: 'Final Publish Approval',
      project: 'Moneyly',
      requestedBy: 'PublisherAgent',
      confidence: 0.99,
      status: 'pending',
      summary: '2,100-word guide targeting "automated payroll tax calculator". Formatted for WordPress REST API.',
      contentPreview: 'Full draft ready for CMS deployment...',
    },
  ];

  const activeApp = approvals.find((a) => a.id === selectedApproval) || approvals[0];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-white">Human In The Loop — Approval Center</h1>
          <p className="text-sm text-slate-400 mt-1">
            Review, edit, and approve AI agent outputs before workflow execution resumes.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pending Queue List (1 col) */}
        <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-4">
          <h3 className="font-display font-semibold text-base text-white">Pending Approvals</h3>
          <div className="space-y-3">
            {approvals.map((a) => (
              <button
                key={a.id}
                onClick={() => setSelectedApproval(a.id)}
                className={`w-full text-left p-4 rounded-lg border transition-all space-y-2 ${
                  selectedApproval === a.id
                    ? 'bg-brand/10 border-brand/40 text-white'
                    : 'bg-background border-surface-border text-slate-300 hover:bg-surface-hover'
                }`}
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-brand font-semibold">{a.project}</span>
                  <span className="font-mono text-accent-amber font-semibold">{a.type}</span>
                </div>
                <p className="text-sm font-medium line-clamp-2">{a.title}</p>
                <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                  <span>Conf: {(a.confidence * 100).toFixed(0)}%</span>
                  <span className="text-slate-500">{a.id}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Inspection & Edit Panel (2 cols) */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-surface border border-surface-border space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-surface-border pb-4">
              <div>
                <span className="text-xs font-mono text-brand">{activeApp.project} • {activeApp.type}</span>
                <h2 className="font-display font-semibold text-lg text-white">{activeApp.title}</h2>
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 rounded-lg bg-surface-border hover:bg-rose-500/20 hover:text-rose-400 text-slate-300 text-xs font-semibold flex items-center gap-1.5 transition-colors">
                  <XCircle className="w-4 h-4 text-rose-500" />
                  Reject & Redraft
                </button>
                <button className="px-4 py-2 rounded-lg bg-accent-emerald hover:bg-emerald-600 text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition-all">
                  <CheckCircle2 className="w-4 h-4" />
                  Approve & Resume Workflow
                </button>
              </div>
            </div>

            {/* Metadata bar */}
            <div className="p-3 rounded-lg bg-background border border-surface-border flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>Agent: <strong className="text-slate-200">{activeApp.requestedBy}</strong></span>
              <span>Confidence: <strong className="text-accent-emerald">{(activeApp.confidence * 100).toFixed(0)}%</strong></span>
              <span>Checkpoint: <strong className="text-slate-200">#chk-8012</strong></span>
            </div>

            {/* Editable Content Area */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Edit3 className="w-3.5 h-3.5 text-brand" />
                Human Override Editor (Changes will merge into Workflow State)
              </label>
              <textarea
                defaultValue={activeApp.contentPreview.trim()}
                rows={14}
                className="w-full p-4 rounded-lg bg-background border border-surface-border font-mono text-xs text-slate-200 focus:outline-none focus:border-brand transition-colors"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
