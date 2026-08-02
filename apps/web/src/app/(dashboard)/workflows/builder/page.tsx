'use client';

import { useState } from 'react';
import { Play, Save, Plus, ArrowRight, Sparkles, Database, Search, FileText, CheckCircle } from 'lucide-react';

export default function WorkflowBuilderPage() {
  const [nodes, setNodes] = useState([
    { id: '1', name: 'SERP Researcher', type: 'Research', agent: 'SERPResearcherAgent', icon: Search },
    { id: '2', name: 'Evidence Collector', type: 'Knowledge', agent: 'EvidenceCollectorAgent', icon: Database },
    { id: '3', name: 'Markdown Writer', type: 'Content', agent: 'WriterAgent', icon: FileText },
    { id: '4', name: 'Fact Checker', type: 'Audit', agent: 'FactCheckerAgent', icon: CheckCircle },
  ]);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-mono text-brand">LangGraph Visual Studio</span>
          <h1 className="font-display font-bold text-2xl text-white">Dynamic Workflow Graph Builder</h1>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 rounded-lg bg-surface-border hover:bg-surface-hover text-white text-sm font-semibold flex items-center gap-2 transition-colors">
            <Save className="w-4 h-4" /> Save Graph
          </button>
          <button className="px-4 py-2 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-brand/20 transition-all">
            <Play className="w-4 h-4" /> Compile & Run
          </button>
        </div>
      </div>

      {/* Visual Canvas */}
      <div className="p-8 rounded-xl bg-surface border border-surface-border min-h-[450px] relative flex items-center justify-center overflow-x-auto">
        <div className="flex items-center gap-6">
          {nodes.map((n, idx) => {
            const Icon = n.icon;
            return (
              <div key={n.id} className="flex items-center gap-6">
                <div className="w-64 p-5 rounded-xl bg-background border border-surface-border hover:border-brand/50 transition-all space-y-3 shadow-xl">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-brand/10 text-brand border border-brand/20">
                      {n.type}
                    </span>
                    <Icon className="w-4 h-4 text-slate-400" />
                  </div>
                  <h3 className="font-display font-semibold text-base text-white">{n.name}</h3>
                  <p className="text-xs text-slate-400 font-mono">{n.agent}</p>
                </div>
                {idx < nodes.length - 1 && (
                  <ArrowRight className="w-6 h-6 text-brand animate-pulse" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
