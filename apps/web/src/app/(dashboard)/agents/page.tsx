'use client';

import { Cpu, Plus, Settings, ShieldCheck, Sparkles } from 'lucide-react';

export default function AgentStudioPage() {
  const agents = [
    { name: 'SiteAnalyzerAgent', cat: 'Ingestion', version: 'v1.0.0', conf: '98%', model: 'gpt-4o' },
    { name: 'KnowledgeBuilderAgent', cat: 'PKL Engine', version: 'v1.0.0', conf: '99%', model: 'gpt-4o' },
    { name: 'SERPResearcherAgent', cat: 'Research', version: 'v1.0.0', conf: '97%', model: 'gpt-4o' },
    { name: 'EvidenceCollectorAgent', cat: 'Research', version: 'v1.0.0', conf: '97%', model: 'gpt-4o' },
    { name: 'WriterAgent', cat: 'Writing', version: 'v1.0.0', conf: '96%', model: 'claude-3-5-sonnet' },
    { name: 'FactCheckerAgent', cat: 'Review', version: 'v1.0.0', conf: '99%', model: 'gpt-4o' },
    { name: 'BrandReviewerAgent', cat: 'Review', version: 'v1.0.0', conf: '98%', model: 'gpt-4o' },
    { name: 'LLMAsAJudge', cat: 'Audit', version: 'v1.0.0', conf: '99%', model: 'gpt-4o' },
  ];

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-white">Agent Studio</h1>
          <p className="text-sm text-slate-400 mt-1">Manage single-responsibility specialized AI agents, prompts, and tool policies.</p>
        </div>
        <button className="px-4 py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-brand/20 transition-all">
          <Plus className="w-4 h-4" /> Register New Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {agents.map((a) => (
          <div key={a.name} className="p-5 rounded-xl bg-surface border border-surface-border space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-brand/10 text-brand border border-brand/20">{a.cat}</span>
              <span className="text-xs font-mono text-slate-500">{a.version}</span>
            </div>
            <h3 className="font-display font-semibold text-base text-white">{a.name}</h3>
            <div className="text-xs text-slate-400 pt-2 border-t border-surface-border flex justify-between">
              <span>Model: <strong className="text-slate-200">{a.model}</strong></span>
              <span className="text-accent-emerald font-mono">{a.conf}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
