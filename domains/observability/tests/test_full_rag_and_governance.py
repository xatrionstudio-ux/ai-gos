"""
End-to-end integration test suite verifying AGOS specifications 08, 09, 10, and 11.
"""

import pytest
import uuid

from domains.knowledge.infrastructure.hybrid_rag import AntiHallucinationLayer, HybridRAGEngine, HybridSearchQuery
from domains.memory.domain.entities.memory import MemoryLayerType
from domains.memory.domain.memory_broker import MemoryBroker
from domains.observability.domain.cost_tracker import AICostTracker
from domains.observability.domain.llm_as_a_judge import JudgeEvaluationRequest, LLMAsAJudge
from packages.tools.tool_broker import ToolBroker, ToolExecutionRequest


@pytest.mark.asyncio
async def test_memory_broker_7_layers():
    broker = MemoryBroker()
    org_id = uuid.uuid4()
    project_id = uuid.uuid4()

    broker.store_memory(org_id=org_id, project_id=project_id, layer=MemoryLayerType.WORKING, key="state", content={"step": "writing"})
    broker.store_memory(org_id=org_id, project_id=project_id, layer=MemoryLayerType.PROJECT, key="brand", content={"tone": "Authoritative"})

    context = broker.assemble_context(org_id=org_id, project_id=project_id, max_token_budget=32000)
    assert context["assembled"] is True
    assert len(context["working_memory"]) == 1
    assert len(context["project_memory"]) == 1


@pytest.mark.asyncio
async def test_tool_broker_permissions_and_fallback():
    broker = ToolBroker()

    req = ToolExecutionRequest(
        agent_id="seo_writer",
        capability_needed="web_search",
        allowed_tools=["search"],
        forbidden_tools=["billing"],
        params={"query": "hypnotherapy"},
    )
    res = await broker.execute_intent(req)
    assert res.success is True
    assert res.provider_used == "Tavily"
    assert res.cost_usd > 0


@pytest.mark.asyncio
async def test_hybrid_rag_and_anti_hallucination_gate():
    rag = HybridRAGEngine()
    query = HybridSearchQuery(project_id=uuid.uuid4(), query="TranceOS features")
    pack = await rag.search_and_assemble(query)

    assert pack.total_evidence_count > 0
    passed, msg = AntiHallucinationLayer.verify_evidence_density(pack)
    assert passed is True
    assert msg == "VERIFIED"


@pytest.mark.asyncio
async def test_llm_as_a_judge_and_cost_tracker():
    judge = LLMAsAJudge()
    art_id = uuid.uuid4()
    eval_res = await judge.process(
        JudgeEvaluationRequest(
            artifact_id=art_id,
            content_markdown="# Guide",
            target_keyword="hypnotherapy",
            pkl_entities=["TranceOS"],
            target_tone="Clinical",
        )
    )
    assert eval_res.result.overall_quality_score > 90.0
    assert eval_res.result.is_production_ready is True

    tracker = AICostTracker()
    org_id = uuid.uuid4()
    policy = tracker.record_cost(org_id, cost_usd=0.50)
    assert policy.current_daily_spend_usd == 0.50
