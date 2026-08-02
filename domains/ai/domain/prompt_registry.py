"""
PromptRegistry — versioned prompt template manager.

Prompts are stored with semantic versioning and Git SHA references.
Never hardcode prompts inside agent logic!
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from core.base_entity import BaseEntity
from core.exceptions import NotFoundError


class PromptVersion(BaseEntity):
    name: str = Field(description="e.g. writer_agent")
    version: str = Field(description="semver, e.g. 1.2.0")
    git_sha: str | None = None
    template: str = Field(description="Jinja2 or str.format template")
    variables: list[str] = Field(default_factory=list)
    model_target: str | None = None


class PromptRegistry:
    """In-memory and DB-backed Prompt Registry."""

    _prompts: dict[str, dict[str, PromptVersion]] = {}

    @classmethod
    def register(cls, prompt: PromptVersion) -> None:
        if prompt.name not in cls._prompts:
            cls._prompts[prompt.name] = {}
        cls._prompts[prompt.name][prompt.version] = prompt

    @classmethod
    def get(cls, name: str, version: str = "latest") -> PromptVersion:
        if name not in cls._prompts:
            raise NotFoundError(f"Prompt template '{name}' not found in registry.")

        versions = cls._prompts[name]
        if version == "latest":
            latest_ver = sorted(versions.keys())[-1]
            return versions[latest_ver]

        if version not in versions:
            raise NotFoundError(f"Prompt template '{name}' version '{version}' not found.")

        return versions[version]

    @classmethod
    def render(cls, name: str, version: str = "latest", **kwargs: Any) -> tuple[str, PromptVersion]:
        prompt_ver = cls.get(name, version)
        rendered = prompt_ver.template.format(**kwargs)
        return rendered, prompt_ver
