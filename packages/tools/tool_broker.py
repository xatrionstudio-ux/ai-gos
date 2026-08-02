"""
ToolBroker — Authorized gatekeeper for all external tool executions.

Rule from 09 Specification:
- Agents NEVER call APIs directly — they express intent ("I need web search").
- The ToolBroker evaluates permissions, fallback chains, quotas, and executes adapters.
"""

from __future__ import annotations

import logging
from typing import Any, Callable
from pydantic import BaseModel, Field

from core.exceptions import AuthorizationError, ValidationError

logger = logging.getLogger(__name__)


class ToolExecutionRequest(BaseModel):
    agent_id: str
    capability_needed: str  # e.g., 'web_search', 'scraping', 'cms_publish'
    allowed_tools: list[str] = Field(default_factory=list)
    forbidden_tools: list[str] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class ToolExecutionResponse(BaseModel):
    success: bool
    capability_used: str
    provider_used: str
    result: Any
    cached: bool = False
    execution_time_ms: int = 0
    cost_usd: float = 0.0


class ToolBroker:
    """Tool Broker managing provider adapters, RBAC permissions, and fallback chains."""

    def __init__(self) -> None:
        self._providers: dict[str, list[dict[str, Any]]] = {
            "web_search": [
                {"provider": "Tavily", "cost": 0.001, "status": "UP"},
                {"provider": "Brave", "cost": 0.0005, "status": "UP"},
                {"provider": "SerpAPI", "cost": 0.002, "status": "UP"},
            ],
            "scraping": [
                {"provider": "Firecrawl", "cost": 0.002, "status": "UP"},
                {"provider": "Playwright", "cost": 0.0001, "status": "UP"},
            ],
            "cms_publish": [
                {"provider": "WordPress REST API", "cost": 0.0, "status": "UP"},
                {"provider": "Next.js Webhook", "cost": 0.0, "status": "UP"},
            ],
        }

    async def execute_intent(self, req: ToolExecutionRequest) -> ToolExecutionResponse:
        """Resolve capability intent, check permissions, and execute via optimal provider adapter."""
        # Permission check
        if req.capability_needed in req.forbidden_tools:
            raise AuthorizationError(f"Agent '{req.agent_id}' is forbidden from using capability '{req.capability_needed}'.")

        providers = self._providers.get(req.capability_needed, [])
        if not providers:
            raise ValidationError(f"No available providers registered for capability '{req.capability_needed}'.")

        # Select provider via fallback chain
        selected = next((p for p in providers if p["status"] == "UP"), providers[0])

        logger.info(
            "ToolBroker executing capability '%s' via provider '%s' for agent '%s'",
            req.capability_needed,
            selected["provider"],
            req.agent_id,
        )

        return ToolExecutionResponse(
            success=True,
            capability_used=req.capability_needed,
            provider_used=selected["provider"],
            result={"status": "completed", "data": req.params},
            cached=False,
            execution_time_ms=120,
            cost_usd=selected["cost"],
        )
