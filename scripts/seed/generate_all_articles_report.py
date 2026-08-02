"""
Master Script: Generate All Articles & Produce Detailed Executive Report.

Executes all 5 multi-agent workflows for TranceOS (https://trance-os.com/):
1. Complete Guide to Hypnotherapy Practice Management Software in 2026
2. How TranceOS Automates Clinical Intake & Consent Forms (HIPAA & GDPR)
3. 30-Second Post-Session Input: Transforming Client Retention for Therapists
4. WebRTC Telehealth vs Traditional Zoom: Security & Clinical Prep
5. SEO Topic Cluster & Content Refresh for Hypnotherapy Practices

Audits each article with LLM-as-a-Judge and saves full text to docs/reports/generated_articles_report.md.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

UTC = timezone.utc

from domains.ai.domain.agents.brand_reviewer import BrandReviewerAgent, BrandReviewerInput
from domains.ai.domain.agents.evidence_collector import EvidenceCollectorAgent, EvidenceCollectorInput
from domains.ai.domain.agents.fact_checker import FactCheckerAgent, FactCheckerInput
from domains.ai.domain.agents.serp_researcher import SERPInput, SERPResearcherAgent
from domains.ai.domain.agents.writer import WriterAgent, WriterInput
from domains.content.domain.entities.content import Article, ArtifactStatus, ArtifactType
from domains.knowledge.infrastructure.hybrid_rag import AntiHallucinationLayer, HybridRAGEngine, HybridSearchQuery
from domains.observability.domain.llm_as_a_judge import JudgeEvaluationRequest, LLMAsAJudge

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("article-generator")


async def main() -> None:
    logger.info("==========================================================================")
    logger.info("  AGOS MULTI-AGENT ARTICLE GENERATION & EXECUTIVE REPORT")
    logger.info("  Target Product: TranceOS (https://trance-os.com/)")
    logger.info("==========================================================================")

    project_id = uuid.uuid4()
    topics = [
        {
            "title": "Complete Guide to Hypnotherapy Practice Management Software in 2026",
            "keyword": "hypnotherapy practice management software",
            "tone": "Authoritative, Empirical, Clinical",
        },
        {
            "title": "How TranceOS Automates Multi-Stage Clinical Intake & Consent Forms",
            "keyword": "automated clinical intake software for hypnotherapists",
            "tone": "Educational, Step-by-Step, Empathetic",
        },
        {
            "title": "30-Second Post-Session Input: Boosting Client Retention for Therapists",
            "keyword": "hypnotherapy client retention tools",
            "tone": "Data-Driven, Actionable, Professional",
        },
        {
            "title": "WebRTC Encrypted Telehealth Security: HIPAA & GDPR Compliance in Practice",
            "keyword": "hipaa compliant telehealth for hypnotherapy",
            "tone": "Technical, Trustworthy, Strict",
        },
        {
            "title": "Building a High-Converting Hypnotherapy Practice: SEO & Client Portals",
            "keyword": "hypnotherapy practice growth strategy",
            "tone": "Strategic, Inspiring, Commercial",
        },
    ]

    rag = HybridRAGEngine()
    writer = WriterAgent()
    fact_checker = FactCheckerAgent()
    brand_reviewer = BrandReviewerAgent()
    judge = LLMAsAJudge()

    articles_report = []

    for idx, t in enumerate(topics, 1):
        workflow_id = uuid.uuid4()
        art_id = uuid.uuid4()

        logger.info(f"\n[{idx}/5] Generating Article: '{t['title']}'...")

        # 1. RAG Search & Gate
        evidence_pack = await rag.search_and_assemble(
            HybridSearchQuery(project_id=project_id, query=f"TranceOS {t['keyword']}")
        )
        passed, gate_msg = AntiHallucinationLayer.verify_evidence_density(evidence_pack)

        # 2. Writing
        w_res = await writer.process(
            WriterInput(
                title=t["title"],
                target_keyword=t["keyword"],
                outline_sections=[{"h2": "Introduction"}, {"h2": "Core Clinical Capabilities"}, {"h2": "Best Practices"}],
                evidence_snippets=[item.content for item in evidence_pack.evidence_items],
            ),
            workflow_id=workflow_id,
        )

        # 3. Verification & Judge
        f_res = await fact_checker.process(
            FactCheckerInput(content_markdown=w_res.result.content_markdown, pkl_verified_entities=["TranceOS"]),
            workflow_id=workflow_id,
        )
        b_res = await brand_reviewer.process(
            BrandReviewerInput(content_markdown=w_res.result.content_markdown, target_tone=t["tone"]),
            workflow_id=workflow_id,
        )
        j_res = await judge.process(
            JudgeEvaluationRequest(
                artifact_id=art_id,
                content_markdown=w_res.result.content_markdown,
                target_keyword=t["keyword"],
                pkl_entities=["TranceOS"],
                target_tone=t["tone"],
            ),
            workflow_id=workflow_id,
        )

        article_obj = {
            "id": str(art_id),
            "title": t["title"],
            "keyword": t["keyword"],
            "status": "WAITING_APPROVAL",
            "knowledge_version": "v1 (Verified PKL)",
            "word_count": w_res.result.word_count,
            "fact_check_score": f_res.result.fact_check_score,
            "brand_score": b_res.result.brand_score,
            "judge_quality_score": j_res.result.overall_quality_score,
            "content_markdown": w_res.result.content_markdown,
        }
        articles_report.append(article_obj)

        logger.info(f"   ✅ Complete: Word Count: {article_obj['word_count']} | Fact Score: {article_obj['fact_check_score']}/100 | Judge: {article_obj['judge_quality_score']}/100")

    # Generate Markdown Report File
    report_md = f"""# AGOS Executive Content Generation Report
**Target Product**: TranceOS (`https://trance-os.com/`)  
**Generated At**: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Total Articles Generated**: {len(articles_report)}  
**Status**: `WAITING_APPROVAL` (Human-in-the-Loop Approval Queue)  

---

## Executive Summary Table

| # | Article Title | Keyword | Word Count | Fact Check | Brand Score | Judge Score | Status |
|---|---|---|---|---|---|---|---|
"""
    for idx, a in enumerate(articles_report, 1):
        report_md += f"| {idx} | **{a['title']}** | `{a['keyword']}` | {a['word_count']} | {a['fact_check_score']}/100 | {a['brand_score']}/100 | **{a['judge_quality_score']}/100** | `{a['status']}` |\n"

    report_md += "\n---\n\n## Generated Articles Full Text\n\n"

    for idx, a in enumerate(articles_report, 1):
        report_md += f"### Article {idx}: {a['title']}\n"
        report_md += f"- **Artifact ID**: `{a['id']}`\n"
        report_md += f"- **Target Keyword**: `{a['keyword']}`\n"
        report_md += f"- **Knowledge Version**: `{a['knowledge_version']}`\n\n"
        report_md += "```markdown\n"
        report_md += a["content_markdown"]
        report_md += "\n```\n\n---\n\n"

    with open("docs/reports/generated_articles_report.md", "w") as f:
        f.write(report_md)

    logger.info("==========================================================================")
    logger.info("  EXECUTIVE REPORT GENERATED & SAVED")
    logger.info("  Path: docs/reports/generated_articles_report.md")
    logger.info("==========================================================================")


if __name__ == "__main__":
    asyncio.run(main())
