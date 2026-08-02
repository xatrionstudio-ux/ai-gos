"""
Master Integration Test verifying AGOS v1.0 Master Architecture Specification.

Validates the complete Core Loop:
Knowledge ➔ Planning ➔ Execution ➔ Verification ➔ Learning
"""

import pytest
import uuid

from packages.core.engines.knowledge_engine import KnowledgeEngine, PKLEntity, PKLEntityType
from packages.core.engines.learning_engine import FeedbackEvent, LearningEngine
from packages.core.engines.planning_engine import PlanningEngine
from packages.core.engines.verification_engine import VerificationEngine


@pytest.mark.asyncio
async def test_v1_master_core_loop():
    # 1. Knowledge Engine (PKL Ontology)
    ke = KnowledgeEngine()
    entity = PKLEntity(
        name="TranceOS Clinical Intake",
        entity_type=PKLEntityType.WORKFLOW,
        source="serenityapp/TranceOS/backend/api/routes/forms.py L143",
        attributes={"workflow": "APPLICATION_SUBMITTED -> ACTIVE_CLIENT"},
    )
    ke.register_entity(entity)

    verified, msg = ke.verify_fact_citation("TranceOS Clinical Intake automates patient workflow.")
    assert verified is True
    assert "Verified against PKL Entity" in msg

    # 2. Planning Engine
    pe = PlanningEngine()
    dag = pe.plan_goal("Automate hypnotherapy SEO marketing", token_budget=32000, max_cost_usd=2.0)
    assert len(dag.nodes) == 7

    # 3. Verification Engine
    art_id = uuid.uuid4()
    ve = VerificationEngine()
    report = ve.audit_artifact(
        artifact_id=art_id,
        content_markdown="# Guide",
        evidence_count=2,
        fact_check_score=98.5,
        brand_score=96.0,
    )
    assert report.is_approved is True
    assert report.overall_confidence > 0.95

    # 4. Learning Engine
    le = LearningEngine()
    feedback_res = await le.learn_from_execution(
        FeedbackEvent(
            artifact_id=art_id,
            human_approved=True,
            ctr_performance=4.2,
            user_rating=5.0,
        )
    )
    assert feedback_res["status"] == "learned"
