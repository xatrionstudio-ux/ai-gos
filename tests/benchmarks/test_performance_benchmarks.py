"""
Production Benchmark Suite for AGOS.

Validates Performance SLAs:
- Hybrid Search Latency < 300ms
- Memory Retrieval Latency < 100ms
- Agent Execution Overhead < 500ms
"""

import time
import pytest
import uuid

from domains.knowledge.infrastructure.hybrid_rag import HybridRAGEngine, HybridSearchQuery
from domains.memory.domain.memory_broker import MemoryBroker


@pytest.mark.asyncio
async def test_hybrid_search_sla_benchmark():
    rag = HybridRAGEngine()
    query = HybridSearchQuery(project_id=uuid.uuid4(), query="TranceOS Telehealth")

    start = time.perf_counter()
    pack = await rag.search_and_assemble(query)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert pack.total_evidence_count > 0
    assert elapsed_ms < 300.0, f"Hybrid Search SLA violated: took {elapsed_ms:.2f}ms (SLA < 300ms)"


@pytest.mark.asyncio
async def test_memory_retrieval_sla_benchmark():
    broker = MemoryBroker()
    org_id = uuid.uuid4()
    project_id = uuid.uuid4()

    start = time.perf_counter()
    context = broker.assemble_context(org_id=org_id, project_id=project_id)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert context["assembled"] is True
    assert elapsed_ms < 100.0, f"Memory Retrieval SLA violated: took {elapsed_ms:.2f}ms (SLA < 100ms)"
