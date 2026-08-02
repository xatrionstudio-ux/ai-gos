"""
Official Python SDK for AI Growth Operating System (AGOS).

Usage:
    from agos_sdk import AGOSClient

    client = AGOSClient(api_key="agos_live_...")
    projects = client.projects.list()
    workflow = client.workflows.start(project_id="...", workflow_type="seo_content")
"""

from __future__ import annotations

import httpx
from typing import Any


class AGOSClient:
    """Official Python Client for AGOS REST API."""

    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )

    def health(self) -> dict[str, str]:
        res = self._http.get("/health")
        return res.json()

    def list_projects(self) -> list[dict[str, Any]]:
        res = self._http.get("/v1/projects")
        return res.json().get("items", [])
