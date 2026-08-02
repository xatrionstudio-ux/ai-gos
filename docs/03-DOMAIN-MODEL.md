# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Approved Domain Specification  
**Owner:** Domain Modeling & DDD Architecture Team  

---

## 03 - DOMAIN MODEL

### Ubiquitous Language

| Concept | Definition |
|---|---|
| **Organization** | Company owning one or more SaaS projects (Tenant boundary) |
| **Workspace** | Logical workspace where users collaborate |
| **Project** | A specific SaaS product (e.g., TranceOS, Moneyly, ConstruAI) |
| **Knowledge** | Structured product truth (Documents, Features, FAQs, Schemas) |
| **Agent** | Specialized AI worker unit with single responsibility |
| **Workflow** | Sequence of agents executed via LangGraph state machine |
| **Task** | Individual unit of work inside a workflow node |
| **Event** | Immutable domain occurrence emitted across the system |
| **Prompt** | Versioned specification sent to the AI model |
| **Tool** | External integration or capability exposed to an agent |
| **Memory** | Persistent shared context (Short, Long, Knowledge, Semantic) |
| **Artifact** | Any generated output (Blog, Landing Page, FAQ, API Doc, etc.) |

---

### Domain Hierarchy

```
Organization
│
├── Workspace
│
├── Users
│
├── Projects
│      ├── Knowledge
│      ├── Agents
│      ├── Workflows
│      ├── Prompts
│      ├── Analytics
│      ├── Artifacts
│      ├── Events
│      └── Memories
│
└── Billing
```

---

### Aggregate Roots

- **`Organization Aggregate`**: ID, Name, Plan, Owner, Settings, Projects, Members, Billing.
- **`Project Aggregate`**: ID, Name, Slug, Brand, Website, Knowledge, Analytics, Settings.
- **`Knowledge Aggregate`**: ID, Version, Entities, Relations, Documents, Features, FAQs, API Docs.
- **`Artifact Aggregate`**: ID, Type, Title, Content, Version, Language, Status, SEO Score, Published At.
- **`Agent Aggregate`**: ID, Name, Version, Description, Prompt, Capabilities, Allowed Tools, Policies.
- **`Prompt Aggregate`**: ID, Version, Variables, Instructions, System Prompt, History (Never overwritten!).
- **`Tool Aggregate`**: ID, Name, Description, Authentication, Limits, Cost, Status.
- **`Workflow Aggregate`**: ID, Name, State, Nodes, Edges, Current Step, Memory, Metrics, Status.
- **`Event Aggregate`**: ID, Type, Source, Payload, Correlation ID, Trace ID, Timestamp, Version.
- **`Memory Aggregate`**: ID, Type, Scope, Embedding, Metadata, Expires, Project.

---

### Domain Lifecycles

#### Artifact Lifecycle
```
Draft ──► Research ──► Outline ──► Writing ──► Review ──► SEO ──► Approval ──► Publishing ──► Monitoring ──► Refreshing
```

#### Knowledge Lifecycle
```
Document Ingested ──► Parsing ──► Chunking ──► Embedding ──► Entity Extraction ──► Relationship Mapping ──► PKL Updated ──► Event Emitted
```

#### Workflow Lifecycle
```
Created ──► Scheduled ──► Running ──► Checkpoint ──► Paused ──► Resumed ──► Completed / Failed
```

---

### Business Rules (Domain Invariants)

1. **Rule 001**: An Artifact must always be associated with a specific, immutable version of Knowledge.
2. **Rule 002**: A Workflow can NEVER mutate Knowledge directly — it must emit domain events.
3. **Rule 003**: AI Agents never access the database directly — always via domain application services.
4. **Rule 004**: Prompts are NEVER overwritten in place — they are strictly semver-versioned.
5. **Rule 005**: Every published artifact must be fully traceable (*Which prompt, model, workflow, agent, and knowledge version generated it*).
6. **Rule 006**: LLM models never receive raw secrets — tool access goes through the AI Gateway.
7. **Rule 007**: Projects never share memory by default — memory is strictly isolated by Organization and Project.

---

### Permission Model & Multi-Tenancy

```
Tenant ──► Organization ──► Workspace ──► Project ──► Knowledge / Artifacts / Workflows
```

#### Roles
- `Owner`: Full platform control
- `Admin`: Full project & team control
- `Editor`: Knowledge & Content editing
- `Reviewer`: Human-in-the-Loop (HITL) approval authority
- `Analyst`: Analytics & SEO monitoring
- `Developer`: API keys & Webhook management
- `Viewer`: Read-only access
- `AI Operator`: Workflow triggering & execution control
