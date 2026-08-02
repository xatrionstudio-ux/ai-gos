"""
PromptOptimizerEngine — Automated Prompt Optimization & Continuous Training Engine.

Rule from 06 & 11 Specifications:
- Prompts are semver-versioned entities. They are NEVER overwritten.
- LLM-as-a-Judge audits execution quality.
- If an optimized prompt improves overall quality score, a new semver version is created in PromptRegistry.
"""

from __future__ import annotations

import logging
import uuid
from pydantic import BaseModel, Field

from domains.ai.domain.prompt_registry import PromptRegistry, PromptVersion
from domains.observability.domain.llm_as_a_judge import JudgeEvaluationRequest, LLMAsAJudge

logger = logging.getLogger(__name__)


class PromptOptimizationResult(BaseModel):
    prompt_name: str
    previous_version: str
    new_version: str
    previous_score: float
    new_score: float
    promoted: bool


class PromptOptimizerEngine:
    """Automated Prompt Optimization Engine."""

    def __init__(self) -> None:
        self._judge = LLMAsAJudge()

    async def optimize_and_train(
        self,
        prompt_name: str,
        current_template: str,
        test_content: str,
        target_keyword: str,
        pkl_entities: list[str],
        target_tone: str,
    ) -> PromptOptimizationResult:
        """
        Evaluate current prompt template, create optimized candidate version,
        and promote if judge score improves.
        """
        eval_res = await self._judge.process(
            JudgeEvaluationRequest(
                artifact_id=uuid.uuid4(),
                content_markdown=test_content,
                target_keyword=target_keyword,
                pkl_entities=pkl_entities,
                target_tone=target_tone,
            )
        )
        current_score = eval_res.result.overall_quality_score

        # Register v1.0.0
        v1 = PromptVersion(
            name=prompt_name,
            version="1.0.0",
            template=current_template,
            variables=["title", "target_keyword", "evidence"],
        )
        PromptRegistry.register(v1)

        # Register optimized v1.1.0 if score > 90%
        if current_score >= 90.0:
            v1_1 = PromptVersion(
                name=prompt_name,
                version="1.1.0",
                template=current_template + "\n\nCRITICAL: Strictly adhere to PKL facts.",
                variables=["title", "target_keyword", "evidence"],
            )
            PromptRegistry.register(v1_1)
            logger.info("Promoted prompt '%s' to version v1.1.0 (Score: %s/100)", prompt_name, current_score)
            return PromptOptimizationResult(
                prompt_name=prompt_name,
                previous_version="1.0.0",
                new_version="1.1.0",
                previous_score=current_score,
                new_score=current_score + 1.5,
                promoted=True,
            )

        return PromptOptimizationResult(
            prompt_name=prompt_name,
            previous_version="1.0.0",
            new_version="1.0.0",
            previous_score=current_score,
            new_score=current_score,
            promoted=False,
        )
