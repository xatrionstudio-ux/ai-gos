# AI Growth Operating System (AI-GOS)

> Production-grade, event-driven, multi-tenant AI operating system designed to autonomously research, plan, write, validate, publish, and improve content across multiple SaaS products.

---

## Key Capabilities

- **Product Knowledge Layer (PKL)** — Single source of truth. Continuous ingestion of site, docs, Notion, GitHub, release notes, and FAQs. Agents never hallucinate features.
- **26 Specialized AI Agents** — Single-responsibility agents (Site Analyzer, SERP Researcher, Competitor Analyst, Outline Generator, Writer, Fact Checker, Legal Reviewer, Brand Reviewer, Publisher, etc.).
- **LangGraph Orchestration** — State-machine execution, automatic checkpoints, human-in-the-loop (HITL) approval gates, resume/rollback capabilities.
- **Multi-Tenant Security** — PostgreSQL Row-Level Security (RLS), RS256 asymmetric JWT authentication, RBAC permission system, Argon2id password hashing.
- **Observability Built-In** — OpenTelemetry tracing, Prometheus metrics, Grafana dashboards, token & USD cost tracking per agent call.

---

## Monorepo Architecture

```
ai-gos/
├── apps/
│   ├── api/             # FastAPI gateway (thin routing, OpenAPI)
│   ├── worker/          # Celery task processing pool
│   ├── scheduler/       # Celery Beat / RedBeat scheduler
│   └── web/             # Next.js 14 App Router frontend
│
├── packages/
│   ├── core/            # Base entities, repository interfaces, Result monad
│   ├── events/          # Domain events, event bus, dual-dispatch engine
│   └── sdk/             # Client SDKs
│
├── domains/             # 15 Bounded Contexts (DDD + Clean Architecture)
│   ├── identity/        # Auth, JWT RS256, Users, Organizations, Roles
│   ├── projects/        # SaaS product profiles, brand voice, CMS settings
│   ├── knowledge/       # Product Knowledge Layer (RAG, vector store)
│   ├── research/        # SERP, multi-source evidence collector
│   ├── seo/             # Keywords, topic clusters, Schema.org
│   ├── content/         # Articles, versioning, diffs
│   ├── publishing/      # CMS adapters (Next.js, WordPress, Ghost, Webflow)
│   ├── analytics/       # GSC, GA4, Plausible, content decay detection
│   ├── workflow/        # LangGraph state machine, checkpoints, HITL
│   └── ai/              # BaseAgent, PromptRegistry, LLMRouter, Cost Logger
│
└── infrastructure/
    ├── docker/          # Production Dockerfiles & compose
    ├── nginx/           # Reverse proxy, rate limiting, CSP, SSE
    └── kubernetes/      # K8s manifests
```

---

## Quickstart Guide

### Prerequisites
- Docker & Docker Compose
- OpenSSL (for RS256 keys)
- Python >= 3.12 (optional for local dev outside Docker)
- Node.js >= 20 & pnpm (optional for local dev outside Docker)

### 1. Initialize Keys & Environment
```bash
# Clone or navigate to repository
cd /Users/estebanescobar/ai-gos

# Generate JWT RS256 key pair
make keys

# Create .env file
cp .env.example .env
```

### 2. Launch All Services (Docker Compose)
```bash
make dev-bg
```

Services started:
| Service | URL | Purpose |
|---|---|---|
| Web Frontend | `http://localhost:3000` | Next.js Dashboard |
| API Gateway | `http://localhost:8000` | FastAPI REST API |
| API Docs | `http://localhost:8000/docs` | OpenAPI Specification |
| Grafana | `http://localhost:3001` | Observability Dashboards |
| Prometheus | `http://localhost:9090` | Metrics Storage |
| Flower | `http://localhost:5555` | Celery Worker Monitor |

---

## Verification & Testing

```bash
# Run unit & integration tests inside container
make test

# Lint code
make lint

# Run security secret scan
make secrets-scan
```
