# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Production Design  
**Owner:** Platform Engineering  

---

## 05 - DATABASE ARCHITECTURE

### Philosophy

The database does **NOT** store raw articles, prompts, or chat logs as static strings. The database stores the complete, structured knowledge of a business and all agent execution telemetry. Generated content is merely an observable consequence of knowledge.

---

### Polyglot Storage Stack

```
                    PostgreSQL
                Source of Truth
                      │
      ────────────────┼────────────────
                      │
                  Redis Cache
                      │
      ────────────────┼────────────────
                      │
             Qdrant Vector Database
                      │
      ────────────────┼────────────────
                      │
             S3 / Local Object Storage
```

- **PostgreSQL**: Primary Source of Truth (Entities, Relations, Workflows, Audit Logs, Organizations, Projects, RLS).
- **Redis**: Caching, distributed locks, rate limiting, pub/sub event bus, Celery queue.
- **Qdrant**: Vector embeddings, high-dimensional similarity search, hybrid reranking.
- **S3 / Local Storage**: Uploaded documents (PDFs, Markdown, images, video assets, HTML snapshots).

---

### Global Entity ERD Schema

```
Organization ──► Workspace ──► Project ──► Knowledge Base ──► Knowledge Assets
                                  │                             │
                                  ├─► Entities ◄────────────────┘
                                  ├─► Artifacts ──► Publications
                                  ├─► Analytics
                                  └─► Workflows ──► Workflow Nodes & Checkpoints
```

---

### Multi-Tenant Strategy

- Every database query filters by `organization_id` and `project_id`.
- PostgreSQL Row-Level Security (RLS) policies enforce tenant boundary isolation at the database level.
- Critical entities use **soft deletion** (`deleted_at`, `deleted_by`) — physical deletes are forbidden.

---

### Data Retention & Index Strategy

- **Event Store**: Immutable, append-only, permanent.
- **Audit Logs**: Configurable per organization plan.
- **Artifacts**: Full version history preserved.
- **Indexes**: Composite indexes on `(organization_id, project_id)`, `(workflow_id, node_id)`, `(trace_id)`.
