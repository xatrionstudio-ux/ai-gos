# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Approved Architecture Specification  
**Owner:** Platform Engineering  

---

## 04 - MICROSERVICES ARCHITECTURE

### Philosophy

- Each microservice has a single responsibility.
- Never share database instances across services.
- Never share business logic across boundaries.
- Never make direct synchronous calls to another microservice to execute business logic — always communicate via events whenever possible.

---

### Global Service Map

```
                                     Users
                                       │
                                       ▼
                                API Gateway
                                       │
        ───────────────────────────────┼──────────────────────────────
                                       │
      Identity Service         Organization Service        Billing Service
                                       │
                                       ▼
                               Project Service
                                       │
               ────────────────────────┼────────────────────────
                                       │
      Workflow Service        Knowledge Service      Analytics Service
              │                       │                      │
              ▼                       ▼                      ▼
      Agent Runtime           Vector Engine          Reporting Engine
              │
              ▼
        AI Gateway
              │
 ─────────────┼────────────────────────────────────────────
              │
 OpenAI    Claude    Gemini    Local Models
```

---

### Core Microservices

#### 1. Identity Service
- **Responsibility**: Authentication, Authorization, JWT (RS256), OAuth, API Keys, RBAC permissions, MFA.
- **Endpoints**: `POST /v1/auth/login`, `POST /v1/auth/logout`, `POST /v1/auth/refresh`, `GET /v1/auth/me`, `POST /v1/auth/apikey`.
- **Events Published**: `user.created`, `user.deleted`, `user.logged_in`, `apikey.created`.

#### 2. Organization Service
- **Responsibility**: Manage organizations, members, invitations, plans, settings.
- **Endpoints**: `POST /v1/organizations`, `GET /v1/organizations`, `PATCH /v1/organizations`, `DELETE /v1/organizations`.
- **Events Published**: `organization.created`, `organization.updated`, `organization.deleted`.

#### 3. Project Service
- **Responsibility**: Manage SaaS products (e.g., TranceOS, Moneyly, ConstruAI), brand profiles, domains, CMS integrations.
- **Events Published**: `project.created`, `project.updated`, `project.deleted`.

#### 4. Knowledge Service (Core PKL Engine)
- **Responsibility**: Build and maintain the Single Source of Truth for product capabilities. Never generates unverified content.
- **Sources Ingested**: Website, GitHub, Notion, Markdown, OpenAPI, PDF, Support Tickets, Roadmaps, Figma.
- **Pipeline**: `Document` ➔ `Parser` ➔ `Chunker` ➔ `Entity Extraction` ➔ `Embeddings` ➔ `Relationship Detection` ➔ `Knowledge Graph` ➔ `Vector Index`.
- **Endpoints**: `POST /v1/knowledge/import`, `GET /v1/knowledge`, `POST /v1/knowledge/search`, `POST /v1/knowledge/reindex`.
- **Events Published**: `knowledge.created`, `knowledge.updated`, `knowledge.deleted`, `feature.detected`, `documentation.updated`.

#### 5. Vector Service
- **Responsibility**: Embeddings, similarity search, semantic search, reranking (Qdrant engine).
- **Endpoints**: `POST /v1/embed`, `POST /v1/search`, `POST /v1/rerank`.

#### 6. Research Service
- **Responsibility**: Search evidence across Google, Bing, Reddit, YouTube, GitHub, Wikipedia, Government, Academic. Never writes articles.
- **Events Published**: `research.completed`, `research.failed`.

#### 7. AI Gateway
- **Responsibility**: Unified provider-agnostic router. All model calls MUST pass through here.
- **Adapters**: OpenAI, Anthropic, Gemini, Mistral, Llama.
- **Capabilities**: `generate()`, `stream()`, `embed()`, `moderate()`.

#### 8. Prompt Service
- **Responsibility**: Manage semver-versioned prompt templates, variables, evaluations, system prompts. Never overwrites existing prompts.
- **Events Published**: `prompt.created`, `prompt.updated`, `prompt.archived`.

#### 9. Agent Registry
- **Responsibility**: Declarative agent registration (ID, version, capabilities, allowed tools, policies, model requirements).

#### 10. Workflow Service (LangGraph Runtime)
- **Responsibility**: Workflow compilation, state persistence, checkpoints, retries, resume, rollback, HITL pause.
- **States**: `Pending`, `Running`, `Paused`, `Waiting Approval`, `Completed`, `Cancelled`, `Failed`.
- **Events Published**: `workflow.started`, `workflow.paused`, `workflow.completed`, `workflow.failed`.

#### 11. SEO Service
- **Responsibility**: Keyword planning, topic clusters, internal linking, Schema.org JSON-LD generator, AEO & GEO optimization.

#### 12. Content Service
- **Responsibility**: Artifact creation (Blog, Landing, FAQ, Newsletter, API Docs, Case Study, Release Notes). Never researches or publishes.

#### 13. Publishing Service
- **Responsibility**: Deployment to target CMS (Next.js, WordPress, Ghost, Webflow, Shopify, Framer, Webhooks).

#### 14. Analytics Service
- **Responsibility**: Metric centralization (GA4, Google Search Console, Plausible, PostHog, Clarity).
- **Events Published**: `traffic.dropped`, `ranking.improved`, `content.decayed`.

#### 15. Notification & Approval Services
- **Responsibility**: Human in the loop approval tracking and multi-channel notifications (Email, Slack, Webhook).

#### 16. Observability Service
- **Responsibility**: Telemetry logging for every AI invocation (prompt, response, model, latency, cost, tokens, workflow ID, trace ID).
