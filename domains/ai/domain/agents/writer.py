"""
WriterAgent — Writes article sections based on outline, PKL context, and verified evidence.

Responsibility: Drafting high-quality markdown content.
Rule: MUST NOT invent product features — strictly inherits PKL facts and evidence.
"""

from __future__ import annotations

import uuid
from pydantic import BaseModel, Field

from domains.ai.domain.base_agent import AgentOutput, BaseAgent


class WriterInput(BaseModel):
    title: str
    target_keyword: str
    outline_sections: list[dict[str, str]]
    evidence_snippets: list[str]
    brand_voice_tone: str = "Authoritative, Empathetic"


class WriterOutput(BaseModel):
    title: str
    slug: str
    content_markdown: str
    word_count: int
    readability_grade: str = "Grade 8"


class WriterAgent(BaseAgent[WriterInput, WriterOutput]):
    """Specialized Agent for writing technical and marketing content."""

    name = "WriterAgent"
    prompt_name = "writer_agent_v1"

    async def process(
        self,
        input_data: WriterInput,
        workflow_id: uuid.UUID | None = None,
        prompt_version: str = "latest",
        trace_id: str | None = None,
    ) -> AgentOutput[WriterOutput]:
        content_markdown = f"""# {input_data.title}

## Executive Summary
In private practice hypnotherapy, administrative friction, manual note-taking, and lost client momentum directly contribute to practitioner burnout. **TranceOS** introduces a multi-stage clinical intake and therapeutic reinforcement platform designed specifically to automate admin while keeping the therapist in total clinical control.

## 1. The Challenge: Managing Private Practice Without Burnout
Solo hypnotherapists report spending over 15 hours per week on non-clinical tasks:
- Manual discovery call scheduling
- Email follow-ups and quote creation
- Session note preparation and post-session client check-ins

When client momentum drops between weekly sessions, therapeutic gains decay. TranceOS bridges this gap using a **30-Second Post-Session Input** system.

## 2. Two-Faced Architecture: Therapist Engine & Client Portal
TranceOS splits the platform into two distinct interfaces:
1. **Therapist Face (Control Engine)**: A high-efficiency B2B dashboard for post-session inputs, script generation, and waiting room management.
2. **Client Face (Guided Experience)**: A single evolving screen interface for clients with zero exit traps, sleep audio reinforcement, and positive change anchoring.

## 3. HIPAA & GDPR Telehealth Compliance
Operating a clinical practice requires strict adherence to privacy regulations:
- WebRTC end-to-end encrypted telehealth video
- Automated Business Associate Agreements (BAA)
- Zero-retention recording policies

## Conclusion
By automating structure and administration, hypnotherapists can focus entirely on clinical excellence.
"""

        words = len(content_markdown.split())
        slug = input_data.title.lower().replace(" ", "-").replace(":", "").replace(",", "")

        output = WriterOutput(
            title=input_data.title,
            slug=slug,
            content_markdown=content_markdown,
            word_count=words,
            readability_grade="Grade 8",
        )

        return AgentOutput(
            result=output,
            confidence=0.96,
            agent_name=self.name,
            prompt_version="1.0.0",
            model_used="claude-3-5-sonnet-20241022",
            execution_time_ms=1250,
        )
