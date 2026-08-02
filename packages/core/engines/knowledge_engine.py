"""
KnowledgeEngine — Core Engine 1 of AGOS v1.0.

Builds and maintains the Product Knowledge Layer (PKL) Ontology:
Product ➔ Module ➔ Feature ➔ Capability ➔ Workflow ➔ API ➔ Screen ➔ Business Rule ➔ Compliance ➔ Persona

Each entity contains:
- id, type, version, source, confidence, owner, last_verified, relationships
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

UTC = timezone.utc
from enum import Enum

try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        pass

from typing import Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PKLEntityType(StrEnum):
    PRODUCT = "product"
    MODULE = "module"
    FEATURE = "feature"
    CAPABILITY = "capability"
    WORKFLOW = "workflow"
    API = "api"
    SCREEN = "screen"
    BUSINESS_RULE = "business_rule"
    COMPLIANCE = "compliance"
    PERSONA = "persona"


class PKLEntity(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    entity_type: PKLEntityType
    version: int = 1
    source: str  # e.g., "GitHub README.md L143" or "https://trance-os.com/"
    confidence: float = 1.0
    owner: str = "Platform Engineering"
    last_verified: datetime = Field(default_factory=lambda: datetime.now(UTC))
    relationships: dict[str, str] = Field(default_factory=dict)  # e.g. {"USES": "Stripe"}
    attributes: dict[str, Any] = Field(default_factory=dict)


class KnowledgeEngine:
    """Knowledge Engine managing the enterprise PKL Ontology."""

    def __init__(self) -> None:
        self._ontology: dict[uuid.UUID, PKLEntity] = {}

    def register_entity(self, entity: PKLEntity) -> PKLEntity:
        self._ontology[entity.id] = entity
        logger.info("KnowledgeEngine registered entity '%s' (%s, v%s)", entity.name, entity.entity_type.value, entity.version)
        return entity

    def get_entities_by_type(self, entity_type: PKLEntityType) -> list[PKLEntity]:
        return [e for e in self._ontology.values() if e.entity_type == entity_type]

    def verify_fact_citation(self, fact_claim: str) -> tuple[bool, str]:
        """Verify if a fact claim is supported by an entity in the PKL Ontology."""
        for e in self._ontology.values():
            if e.name.lower() in fact_claim.lower() or any(k.lower() in fact_claim.lower() for k in e.attributes.keys()):
                return True, f"Verified against PKL Entity '{e.name}' ({e.source})"
        return False, "NO_VERIFIED_FACT_FOUND"
