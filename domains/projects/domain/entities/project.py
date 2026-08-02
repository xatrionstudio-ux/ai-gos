"""
Projects Domain Entities.

A Project represents one SaaS product (e.g., TranceOS, Moneyly, ConstruAI).
Each Project owns:
- brand_voice: tone, terminology, target persona, style guidelines
- seo_strategy: target keywords, cluster rules, publishing frequency
- cms_config: CMS adapter settings (Next.js, WordPress, Ghost, Webflow)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from core.base_entity import AggregateRoot, BaseEntity


class BrandVoice(BaseModel):
    """Brand voice and style guidelines for content generation."""

    tone: str = Field(default="professional", description="e.g. authoritative, conversational, energetic")
    archetype: str = Field(default="expert", description="e.g. expert, mentor, innovator")
    dos: list[str] = Field(default_factory=list, description="Things to ALWAYS do in content")
    donts: list[str] = Field(default_factory=list, description="Things to NEVER do (forbidden phrases, competitors)")
    target_persona: str | None = Field(default=None, description="Primary ICP description")
    key_terms: dict[str, str] = Field(default_factory=dict, description="Glossary of product-specific terms")


class SEOStrategy(BaseModel):
    """SEO strategy parameters for a project."""

    primary_keywords: list[str] = Field(default_factory=list)
    secondary_keywords: list[str] = Field(default_factory=list)
    target_locales: list[str] = Field(default_factory=lambda: ["en-US"])
    content_types_enabled: list[str] = Field(
        default_factory=lambda: ["blog", "landing", "faq", "comparison", "changelog"]
    )
    publishing_cadence_per_week: int = Field(default=3, ge=1, le=50)


class CMSConfig(BaseModel):
    """Configuration for CMS deployment adapter."""

    cms_type: str = Field(default="nextjs", description="nextjs | wordpress | ghost | webflow | webhook")
    base_url: str | None = Field(default=None)
    api_endpoint: str | None = Field(default=None)
    credentials_vault_key: str | None = Field(default=None, description="Encrypted credentials key")
    webhook_secret: str | None = Field(default=None)
    extra_headers: dict[str, str] = Field(default_factory=dict)


class Project(AggregateRoot):
    """Project Aggregate Root — represents a managed SaaS product."""

    org_id: uuid.UUID
    name: str = Field(min_length=2, max_length=100)
    website_url: str
    brand_voice: BrandVoice = Field(default_factory=BrandVoice)
    seo_strategy: SEOStrategy = Field(default_factory=SEOStrategy)
    cms_config: CMSConfig = Field(default_factory=CMSConfig)
    status: str = Field(default="active")  # active | archived | onboarding

    def update_brand_voice(self, voice: BrandVoice) -> "Project":
        return self.model_copy(update={"brand_voice": voice, "updated_at": datetime.now(UTC)})

    def update_seo_strategy(self, strategy: SEOStrategy) -> "Project":
        return self.model_copy(update={"seo_strategy": strategy, "updated_at": datetime.now(UTC)})

    def update_cms_config(self, config: CMSConfig) -> "Project":
        return self.model_copy(update={"cms_config": config, "updated_at": datetime.now(UTC)})

    def archive(self) -> "Project":
        return self.model_copy(update={"status": "archived", "updated_at": datetime.now(UTC)})
