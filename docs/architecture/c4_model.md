# AGOS Architecture — C4 Model

> **Level 1: System Context | Level 2: Container | Level 3: Component | Level 4: Code**

---

## 1. Context Diagram (C4 Level 1)

```mermaid
graph TD
    User["SaaS Founder / Growth Engineer"] ──► |HTTP / WebSockets| AGOS["AI Growth Operating System (AGOS)"]
    AGOS ──► |REST API| GSC["Google Search Console"]
    AGOS ──► |REST API| GA4["Google Analytics 4"]
    AGOS ──► |REST / Webhooks| GitHub["GitHub Repositories"]
    AGOS ──► |REST API| WordPress["WordPress / CMS Targets"]
    AGOS ──► |LiteLLM Router| LLMs["LLM Providers (OpenAI, Anthropic, Gemini)"]
```

---

## 2. Container Diagram (C4 Level 2)

```mermaid
graph TD
    Web["Next.js 14 Web Dashboard"] ──► |HTTPS| Gateway["FastAPI Gateway"]
    Gateway ──► |gRPC / Async| Identity["Identity & ABAC Service"]
    Gateway ──► |gRPC / Async| Knowledge["Knowledge Service (PKL Engine)"]
    Gateway ──► |gRPC / Async| Workflow["Workflow Service (LangGraph)"]
    Gateway ──► |gRPC / Async| Content["Content & SEO Service"]
    
    Workflow ──► |Event Bus| Worker["Celery Worker Pool"]
    Worker ──► |Tool Broker| MCP["MCP Gateway & Adapters"]
    
    Knowledge ──► |SQL| Postgres[("PostgreSQL 16 (Source of Truth)")]
    Knowledge ──► |Vectors| Qdrant[("Qdrant Vector DB")]
    Workflow ──► |Cache / Lock| Redis[("Redis 7 Cache & Bus")]
```

---

## 3. Component Diagram (C4 Level 3 — Knowledge Service)

```mermaid
graph TD
    Ingestor["Document Ingestor"] ──► |Parse| Chunker["Semantic Chunker"]
    Chunker ──► |Extract| Extractor["Entity Extractor Agent"]
    Extractor ──► |Embed| Embedder["LiteLLM Embeddings Adapter"]
    Embedder ──► |Write| VectorStore["Qdrant Vector Store"]
    Extractor ──► |Write| GraphStore["PostgreSQL Entity Graph"]
```
