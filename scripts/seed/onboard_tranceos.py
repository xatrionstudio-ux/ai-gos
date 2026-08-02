"""
Onboarding Execution Script for TranceOS (https://trance-os.com/).

Executes Workflow 1:
Website (https://trance-os.com/)
  ↓
Crawler (SiteAnalyzerAgent)
  ↓
Content Extraction
  ↓
Knowledge Graph & PKL (KnowledgeBuilderAgent)
  ↓
Product Summary & Feature Detection
  ↓
Competitor & Persona Detection
  ↓
Blog Focus & Keyword Opportunities
"""

import asyncio
import json
import logging
import sys
import uuid

from domains.ai.domain.agents.knowledge_builder import KnowledgeBuilderAgent, KnowledgeBuilderInput
from domains.ai.domain.agents.site_analyzer import SiteAnalyzerAgent, SiteAnalyzerInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("onboard-tranceos")


async def main() -> None:
    logger.info("===========================================================")
    logger.info("  AI Growth Operating System (AI-GOS)")
    logger.info("  WORKFLOW 1: WEBSITE ONBOARDING — https://trance-os.com/")
    logger.info("===========================================================")

    target_url = "https://trance-os.com/"
    project_id = uuid.uuid4()

    # Step 1: SiteAnalyzerAgent
    logger.info("\n[1/3] Launching SiteAnalyzerAgent...")
    site_agent = SiteAnalyzerAgent()
    site_res = await site_agent.process(SiteAnalyzerInput(website_url=target_url))

    logger.info(f"✅ Crawled website: {site_res.result.website_url}")
    logger.info(f"   Pages Extracted: {site_res.result.total_pages_found}")
    logger.info(f"   Detected Framework: {site_res.result.detected_framework}")
    logger.info(f"   Confidence Score: {site_res.confidence * 100:.1f}%\n")

    # Step 2: KnowledgeBuilderAgent
    logger.info("[2/3] Launching KnowledgeBuilderAgent (PKL Ingestion)...")
    kb_agent = KnowledgeBuilderAgent()
    docs_input = [
        {"title": page.title, "content": page.raw_text}
        for page in site_res.result.pages
    ]

    kb_res = await kb_agent.process(
        KnowledgeBuilderInput(project_id=project_id, raw_documents=docs_input)
    )

    logger.info("✅ Product Knowledge Layer Ingestion Complete!")
    logger.info(f"   Product Summary: {kb_res.result.summary}")
    logger.info(f"   Entities Extracted: {len(kb_res.result.entities)}")
    logger.info(f"   Confidence Score: {kb_res.confidence * 100:.1f}%\n")

    # Step 3: Display Results
    logger.info("===========================================================")
    logger.info("  ONBOARDING RESULTS & KNOWLEDGE GRAPH SUMMARY")
    logger.info("===========================================================\n")

    logger.info("--- EXTRACTED PRODUCT ENTITIES ---")
    for i, entity in enumerate(kb_res.result.entities, 1):
        logger.info(f"  {i}. [{entity.entity_type.upper()}] {entity.name}")
        logger.info(f"     Description: {entity.description}")
        if entity.attributes:
            logger.info(f"     Attributes: {entity.attributes}")
        logger.info("")

    logger.info("--- RECOMMENDED BLOG FOCUS ---")
    for i, topic in enumerate(kb_res.result.blog_focus_recommendation, 1):
        logger.info(f"  {i}. {topic}")

    logger.info("\n--- HIGH-INTENT KEYWORD OPPORTUNITIES ---")
    for i, kw in enumerate(kb_res.result.keyword_opportunities, 1):
        logger.info(f"  {i}. {kw}")

    logger.info("\n===========================================================")
    logger.info("  SUCCESS: TranceOS is now fully onboarded into AI-GOS PKL!")
    logger.info("===========================================================")


if __name__ == "__main__":
    asyncio.run(main())
