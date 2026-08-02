# AI Growth Operating System (AGOS)

**Version:** 1.0  
**Status:** Production Architecture  
**Owner:** AI Runtime Team  

---

## 10 - MEMORY ENGINE & CONTEXT MANAGEMENT

### Philosophy

An LLM does not remember across executions.  
An agent does not remember across executions.  
Memory is a **dedicated enterprise service** managed by the **Memory Broker**.

Agents query memory; they never store memory directly.

---

### 7 Memory Layers

1. **Working Memory**: Active workflow execution state (TTL: 1 hour).
2. **Episodic Memory**: Log of historical events, execution results, and traffic outcomes.
3. **Semantic Memory**: High-dimensional concept embeddings and entity relationships.
4. **Procedural Memory**: Execution recipes and workflow templates.
5. **Project Memory**: Product-specific brand voice, target personas, and SEO strategy.
6. **Organization Memory**: Shared enterprise guidelines, legal policies, and writing style.
7. **User Memory**: Individual user preferences and approval thresholds.

---

### Context Budget Distribution

When constructing the optimal LLM context window:

```
Total Token Budget (e.g. 32,000 tokens)
├── Knowledge Context:    35% (11,200 tokens)
├── Research Evidence:   25% ( 8,000 tokens)
├── Working Memory:      20% ( 6,400 tokens)
├── System Instructions: 10% ( 3,200 tokens)
└── Examples & Memory:   10% ( 3,200 tokens)
```

---

### Dynamic Context Compression & Consolidation

- Automatic memory deduplication and compression when token budgets are exceeded.
- Memory Importance Score (`0.00` to `1.00`).
- Nightly memory consolidation: Merges recent episodic events, summarizes, and updates semantic weights.
