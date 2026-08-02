'use client';

import { useState } from 'react';
import { Search, ExternalLink, ShieldCheck, CheckCircle2, FileCode, Database, GitBranch } from 'lucide-react';

export default function EvidenceExplorerPage() {
  const [selectedClaim, setSelectedClaim] = useState(0);

  const claims = [
    {
      claim: "TranceOS features a 30-second post-session input form for hypnotherapists that updates the client portal with 'What is improving'.",
      sourceType: "GitHub Repository",
      sourceLocation: "serenityapp/TranceOS/backend/api/routes/forms.py (L143-L180)",
      entity: "30-Second Post-Session Input",
      confidence: "100%",
      lastVerified: "2026-08-02 20:50:43 UTC",
    },
    {
      claim: "Client guided portal supports multi-stage intake state machine: APPLICATION_SUBMITTED -> CALL_BOOKED -> ACTIVE_CLIENT.",
      sourceType: "Product Knowledge Layer",
      sourceLocation: "PKL Ontology Entity #87192 (TranceOS State Machine)",
      entity: "State Engine Loop",
      confidence: "99%",
      lastVerified: "2026-08-02 20:50:43 UTC",
    },
    {
      claim: "HIPAA and GDPR compliance telehealth engine uses WebRTC encrypted video with zero-retention recording options.",
      sourceType: "Documentation & Code",
      sourceLocation: "https://trance-os.com/security/compliance",
      entity: "HIPAA & GDPR Telehealth Security",
      confidence: "98%",
      lastVerified: "2026-08-02 20:50:43 UTC",
    },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-mono text-brand">Anti-Hallucination Audit Layer</span>
          <h1 className="font-display font-bold text-2xl text-white">Evidence Explorer</h1>
          <p className="text-sm text-slate-400 mt-1">Trace every generated sentence directly back to its PKL source file line or verified URL.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Claims List */}
        <div className="lg:col-span-5 space-y-3">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-500">Generated Claims & Statements</span>
          {claims.map((c, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedClaim(idx)}
              className={`p-4 rounded-xl border transition-all cursor-pointer space-y-2 ${
                selectedClaim === idx ? 'bg-brand/10 border-brand' : 'bg-surface border-surface-border hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-border text-slate-300">{c.entity}</span>
                <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> {c.confidence} Verified
                </span>
              </div>
              <p className="text-xs text-white line-clamp-2 leading-relaxed font-medium">{c.claim}</p>
            </div>
          ))}
        </div>

        {/* Audit Evidence Card */}
        <div className="lg:col-span-7">
          <div className="p-6 rounded-xl bg-surface border border-surface-border space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-surface-border">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-brand" />
                <h3 className="font-display font-semibold text-base text-white">Verifiable Proof Chain</h3>
              </div>
              <span className="text-xs font-mono text-slate-400">Audit ID: pkl-trace-{selectedClaim + 1}8490</span>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-[10px] font-mono uppercase text-slate-500">Statement Audited</label>
                <p className="text-sm text-slate-200 bg-background p-4 rounded-lg border border-surface-border mt-1 leading-relaxed font-mono">
                  "{claims[selectedClaim].claim}"
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-background border border-surface-border space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 flex items-center gap-1">
                    <FileCode className="w-3 h-3 text-brand" /> Source Type
                  </span>
                  <p className="text-xs font-semibold text-white">{claims[selectedClaim].sourceType}</p>
                </div>
                <div className="p-4 rounded-lg bg-background border border-surface-border space-y-1">
                  <span className="text-[10px] font-mono uppercase text-slate-500 flex items-center gap-1">
                    <Database className="w-3 h-3 text-emerald-400" /> PKL Entity
                  </span>
                  <p className="text-xs font-semibold text-white">{claims[selectedClaim].entity}</p>
                </div>
              </div>

              <div>
                <label className="text-[10px] font-mono uppercase text-slate-500">Exact File & Line Citation</label>
                <div className="flex items-center justify-between p-3 rounded-lg bg-background border border-surface-border mt-1">
                  <span className="text-xs font-mono text-slate-300">{claims[selectedClaim].sourceLocation}</span>
                  <ExternalLink className="w-4 h-4 text-brand cursor-pointer hover:text-brand-hover" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
