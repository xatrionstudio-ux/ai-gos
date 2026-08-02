# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Production Architecture  
**Owner:** Knowledge Platform Team  

---

## 08 - KNOWLEDGE ENGINE & HYBRID RAG ARCHITECTURE

### Philosophy

The fundamental flaw of generic AI tools is asking the LLM "What do you know about my company?" on every request.  
That scales poorly, consumes massive tokens, produces inconsistencies, and causes hallucinations.

AGOS operates in reverse:
1. Builds a continuous, verified **Enterprise Knowledge Graph (PKL)**
2. Executes **Hybrid RAG** across SQL, Knowledge Graph, Semantic Vector, and Keyword signals
3. Ensures the LLM reasons **strictly over verified evidence**

> **The LLM is NEVER the source of truth.**

---

### Knowledge Architecture Pipeline

```
                    External Sources
                           │
     Website      GitHub      Notion      PDFs      APIs
        │            │            │          │        │
        └────────────┼────────────┴──────────┴────────┘
                     ▼
              Ingestion Pipeline
                     ▼
            Normalization Engine (Markdown UTF-8)
                     ▼
      Entity & Relation Extraction
                     ▼
             Knowledge Graph
                     ▼
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 PostgreSQL      Qdrant        Object Store
      │              │              │
      └──────────────┼──────────────┘
                     ▼
             Hybrid Retrieval (SQL + Graph + Vector + BM25)
                     ▼
            Context Assembler & Anti-Hallucination Layer
                     ▼
                 AI Runtime
```

---

### 7 Knowledge Layers

1. **Layer 1: Raw Documents** (HTML, Markdown, PDF, OpenAPI, Issues, Tickets)
2. **Layer 2: Normalized Documents** (Structured Markdown, metadata tags)
3. **Layer 3: Chunks** (Semantic chunking by complete ideas, never arbitrary character counts)
4. **Layer 4: Embeddings** (High-dimensional vector representations)
5. **Layer 5: Entities** (Product features, personas, compliance rules, endpoints)
6. **Layer 6: Relationships** (Ontology linking entities e.g., `Client` ➔ `BOOKS` ➔ `Appointment`)
7. **Layer 7: Knowledge Graph** (Connected enterprise graph)

---

### Hybrid Retrieval Pipeline

AGOS never relies solely on vector search. It merges 4 distinct signals:

```
Query ➔ Intent Detection ➔ Entity Detection ➔ Knowledge Graph Query ➔ Vector Search ➔ SQL Search ➔ BM25 Search ➔ Merge & Rank ➔ Evidence Pack
```

---

### Anti-Hallucination Layer

Before executing LLM generation:
- The Runtime evaluates evidence density for all requested claims.
- If zero verified evidence exists in the PKL, short-circuits execution and returns: `"NO_EVIDENCE_FOUND"`.
- Prevents LLMs from inventing product functionality or non-existent APIs.
