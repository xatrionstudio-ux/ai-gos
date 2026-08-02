# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Approved Architecture Specification  
**Owner:** Platform Architecture Team  

---

## 02 - SYSTEM ARCHITECTURE

### Executive Summary

AGOS is a distributed, event-driven platform that orchestrates hundreds of specialized AI agents to execute business growth workflows.

The architecture is designed for:
- High availability
- Multi-tenancy
- Horizontal scalability
- Complete observability
- Cloud-native deployment
- Independence between modules
- AI decoupled from core business logic

> **There is no single "AI Agent".**  
> There is a platform where agents are pluggable components of the system.

---

### High Level Architecture

```
                             Internet
                                 │
                                 ▼
                           API Gateway
                                 │
                ──────────────────────────────────
                                 │
                  Authentication Service
                                 │
                ──────────────────────────────────
                                 │
               Workflow Orchestrator (LangGraph)
                                 │
        ───────────────┬───────────────┬───────────────
                       │               │
                       ▼               ▼
              Agent Runtime      Event Bus
                       │               │
        ───────────────┼───────────────┼───────────────
                       │               │
               Knowledge Engine    Scheduler
                       │
        ───────────────┼────────────────────────────
                       │
     PostgreSQL     Redis      Qdrant      Object Storage
```

---

### Architecture Style

The platform combines:
- **Domain-Driven Design (DDD)**
- **Hexagonal Architecture (Ports & Adapters)**
- **Event-Driven Architecture (EDA)**
- **Command Query Responsibility Segregation (CQRS)**
- **Repository Pattern**
- **Clean Architecture**

> **Rule:** No business logic in HTTP controllers. All logic lives inside the domain model.

---

### C4 Context Diagram

```
                     User
                      │
                      ▼
          AI Growth Operating System
                      │
 ──────────────────────────────────────────────
 │           External Systems                 │
 │                                            │
 │ Google Search Console                      │
 │ Google Analytics                           │
 │ GitHub                                     │
 │ Notion                                     │
 │ WordPress                                  │
 │ Webflow                                    │
 │ Shopify                                    │
 │ Stripe                                     │
 │ Slack                                      │
 │ Figma                                      │
 │ Firecrawl                                  │
 │ Tavily                                     │
 │ OpenAI                                     │
 │ Anthropic                                  │
 │ Gemini                                     │
 ──────────────────────────────────────────────
```

---

### C4 Container Diagram

```
Browser ──► Next.js Dashboard ──► API Gateway ──► Auth Service
                                                  │
 ┌────────────────┬────────────────┬──────────────┴─────────────────┐
 ▼                ▼                ▼                                ▼
Workflow Svc    Knowledge Svc    Research Svc                   Content / SEO Svcs
 │                │                │                                │
 └────────────────┴────────────────┼────────────────────────────────┘
                                   │
                                   ▼
                       Event Bus (Redis / Celery)
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
   PostgreSQL                   Qdrant                     Object Storage
```

---

### Bounded Contexts

| Bounded Context | Responsibility | Never Allowed To... |
|---|---|---|
| **Identity** | Users, Sessions, JWT, OAuth, RBAC, API Keys | Know anything about SEO or Content |
| **Organizations** | Companies, Plans, Subscriptions, Teams, Billing | Handle AI generation directly |
| **Knowledge** | Single Source of Truth, Document Ingestion, Embedding, Versioning | Generate content without verified facts |
| **Research** | SERP analysis, Competitor research, Evidence collection | Write articles |
| **Content** | Writing, Drafting, Structuring | Execute research directly |
| **SEO** | On-page optimization, Schema.org, Keyword clustering | Write un-optimized drafts |
| **Publishing** | CMS Adapters (WordPress, Next.js, Ghost, Webflow) | Modify Knowledge Layer |
| **Analytics** | Traffic, Conversions, CTR, Decay Detection | Orchestrate workflows directly |
| **Workflow** | Agent Orchestration, Checkpoints, HITL, State | Perform direct database mutations |

---

### Communication Pattern

> **Rule:** Services NEVER call other services directly. Always publish to the **Event Bus**.

```
Feature Created
      │
      ▼
Knowledge Updated
      │
      ▼
Documentation Updated
      │
      ▼
SEO Updated ──► Landing Page Updated ──► Newsletter Created ──► Social Posts Generated
```

#### Event Contract Standard

```json
{
  "event_id": "uuid",
  "tenant_id": "uuid",
  "project_id": "uuid",
  "event_type": "knowledge.updated",
  "source": "knowledge-service",
  "version": 1,
  "payload": {},
  "timestamp": "2026-08-02T19:50:00Z"
}
```

---

### Workflow & LangGraph Engine

Workflows do **NOT** run AI logic themselves; they plan, coordinate, persist state, handle retries, rollbacks, and pause for human approval.

#### LangGraph Dynamic Graph Runtime

Graphs are compiled dynamically based on the target goal:

- **SEO Content Workflow**: `KeywordAgent` ➔ `ResearchAgent` ➔ `EvidenceAgent` ➔ `OutlineAgent` ➔ `WriterAgent` ➔ `SEOAgent` ➔ `FactChecker` ➔ `Publisher`
- **Product Update Workflow**: `KnowledgeAgent` ➔ `FeatureDetector` ➔ `APIAnalyzer` ➔ `DocWriter` ➔ `Reviewer` ➔ `Publisher`

---

### AI Layer (Multi-Provider Adapters)

Models are **never** called directly by domain application code.

```
Application ──► AI Gateway ──► Provider Adapter ──► LLM Model
                                  ├─ OpenAI Adapter
                                  ├─ Anthropic Adapter
                                  ├─ Gemini Adapter
                                  ├─ Mistral Adapter
                                  └─ Local Llama Adapter
```

---

### Memory Architecture (Four Layers)

1. **Short Memory**: Active workflow thread state only.
2. **Long Memory**: Project-wide history and decisions.
3. **Knowledge Memory**: Ingested product documentation & code.
4. **Semantic Memory**: High-dimensional vector embeddings in Qdrant.

---

### Storage Architecture

- **PostgreSQL**: Source of truth (ACID, RLS for multi-tenancy).
- **Redis**: Caching, session management, event bus pub/sub.
- **Qdrant**: High-performance vector search engine.
- **S3 / Local Storage**: Document uploads, asset storage.

---

### Architecture Decision Records (ADRs)

- `ADR-001`: LangGraph over CrewAI (State persistence, HITL, streaming).
- `ADR-002`: PostgreSQL as Primary Source of Truth.
- `ADR-003`: Qdrant for Vector Embeddings.
- `ADR-004`: Event-Driven Architecture with Event Replay.
- `ADR-005`: Multi-Provider AI Gateway (LiteLLM Adapter Pattern).
- `ADR-006`: Hexagonal Ports & Adapters Architecture.
