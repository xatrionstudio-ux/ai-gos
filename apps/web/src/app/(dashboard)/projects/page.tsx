'use client';

import { useState } from 'react';
import { Plus, Globe, Settings, FileText, CheckCircle2, ChevronRight } from 'lucide-react';

export default function ProjectsPage() {
  const [projects] = useState([
    {
      id: 'proj-1',
      name: 'TranceOS',
      websiteUrl: 'https://tranceos.com',
      status: 'active',
      documentsCount: 420,
      publishedArticles: 68,
      brandTone: 'Authoritative, Empathetic, Clinical',
      cmsType: 'Next.js 14',
    },
    {
      id: 'proj-2',
      name: 'Moneyly',
      websiteUrl: 'https://moneyly.io',
      status: 'active',
      documentsCount: 180,
      publishedArticles: 42,
      brandTone: 'Energetic, Concise, Data-Driven',
      cmsType: 'WordPress REST API',
    },
    {
      id: 'proj-3',
      name: 'ConstruAI',
      websiteUrl: 'https://construai.app',
      status: 'onboarding',
      documentsCount: 95,
      publishedArticles: 14,
      brandTone: 'Technical, Direct, Pragmatic',
      cmsType: 'Ghost CMS',
    },
  ]);

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display font-bold text-2xl text-white">SaaS Products & Projects</h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage multi-tenant product knowledge layers, brand voices, and CMS deployment endpoints.
          </p>
        </div>
        <button className="px-4 py-2.5 rounded-lg bg-brand hover:bg-brand-hover text-white text-sm font-semibold flex items-center gap-2 shadow-lg shadow-brand/20 transition-all">
          <Plus className="w-4 h-4" />
          <span>New Product Profile</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((p) => (
          <div
            key={p.id}
            className="p-6 rounded-xl bg-surface border border-surface-border hover:border-surface-hover transition-all space-y-5 flex flex-col justify-between"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-brand/10 border border-brand/20 flex items-center justify-center text-brand font-bold font-display text-lg">
                    {p.name.charAt(0)}
                  </div>
                  <div>
                    <h3 className="font-display font-semibold text-lg text-white">{p.name}</h3>
                    <a
                      href={p.websiteUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="text-xs text-slate-400 hover:text-brand flex items-center gap-1 font-mono"
                    >
                      <Globe className="w-3 h-3" />
                      {p.websiteUrl.replace('https://', '')}
                    </a>
                  </div>
                </div>
                <span className="px-2 py-0.5 text-xs font-mono rounded bg-accent-emerald/20 text-accent-emerald border border-accent-emerald/30">
                  {p.status}
                </span>
              </div>

              <div className="space-y-2 pt-2 border-t border-surface-border text-xs">
                <div className="flex justify-between text-slate-400">
                  <span>Knowledge Base:</span>
                  <span className="font-mono text-slate-200">{p.documentsCount} documents</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Published Content:</span>
                  <span className="font-mono text-slate-200">{p.publishedArticles} articles</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>CMS Target:</span>
                  <span className="font-mono text-brand">{p.cmsType}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Brand Tone:</span>
                  <span className="font-mono text-slate-300 truncate max-w-[180px]">{p.brandTone}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-surface-border flex gap-2">
              <button className="flex-1 py-2 text-xs font-semibold rounded bg-background border border-surface-border hover:bg-surface-hover text-slate-300 transition-colors flex items-center justify-center gap-1.5">
                <Settings className="w-3.5 h-3.5" />
                Configure PKL
              </button>
              <button className="py-2 px-3 text-xs font-semibold rounded bg-brand/10 text-brand border border-brand/20 hover:bg-brand/20 transition-colors">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
