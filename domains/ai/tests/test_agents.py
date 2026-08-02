"""
Unit tests for AGOS specialized agents (SiteAnalyzer, KnowledgeBuilder, SERP, Evidence, Writer, FactChecker, BrandReviewer).
"""

import pytest
import uuid

from domains.ai.domain.agents.brand_reviewer import BrandReviewerAgent, BrandReviewerInput
from domains.ai.domain.agents.evidence_collector import EvidenceCollectorAgent, EvidenceCollectorInput
from domains.ai.domain.agents.fact_checker import FactCheckerAgent, FactCheckerInput
from domains.ai.domain.agents.knowledge_builder import KnowledgeBuilderAgent, KnowledgeBuilderInput
from domains.ai.domain.agents.serp_researcher import SERPInput, SERPResearcherAgent
from domains.ai.domain.agents.site_analyzer import SiteAnalyzerAgent, SiteAnalyzerInput
from domains.ai.domain.agents.writer import WriterAgent, WriterInput


@pytest.mark.asyncio
async def test_site_analyzer_agent():
    agent = SiteAnalyzerAgent()
    res = await agent.process(SiteAnalyzerInput(website_url="https://trance-os.com/"))
    assert res.confidence >= 0.90
    assert res.result.total_pages_found > 0
    assert res.result.detected_framework == "Next.js 14 / FastAPI"


@pytest.mark.asyncio
async def test_knowledge_builder_agent():
    agent = KnowledgeBuilderAgent()
    project_id = uuid.uuid4()
    res = await agent.process(
        KnowledgeBuilderInput(
            project_id=project_id,
            raw_documents=[{"title": "TranceOS Overview", "content": "Therapist Control Engine and Client Guided Portal"}],
        )
    )
    assert res.confidence >= 0.90
    assert len(res.result.entities) >= 5
    assert len(res.result.keyword_opportunities) > 0


@pytest.mark.asyncio
async def test_serp_and_evidence_agents():
    serp_agent = SERPResearcherAgent()
    serp_res = await serp_agent.process(SERPInput(query="hypnotherapy software"))
    assert len(serp_res.result.items) > 0

    evidence_agent = EvidenceCollectorAgent()
    ev_res = await evidence_agent.process(EvidenceCollectorInput(topic="hypnotherapy software", target_keywords=["hypnotherapy"]))
    assert ev_res.result.total_evidence_items > 0
    assert ev_res.result.overall_confidence > 0.90


@pytest.mark.asyncio
async def test_writer_fact_brand_agents():
    writer = WriterAgent()
    w_res = await writer.process(
        WriterInput(
            title="Hypnotherapy Practice Software",
            target_keyword="hypnotherapy software",
            outline_sections=[{"h2": "Overview"}],
            evidence_snippets=["TranceOS automates intake."],
        )
    )
    assert w_res.result.word_count > 100

    fact = FactCheckerAgent()
    f_res = await fact.process(FactCheckerInput(content_markdown=w_res.result.content_markdown, pkl_verified_entities=["TranceOS"]))
    assert f_res.result.is_passed

    brand = BrandReviewerAgent()
    b_res = await brand.process(BrandReviewerInput(content_markdown=w_res.result.content_markdown, target_tone="Authoritative"))
    assert b_res.result.is_passed
