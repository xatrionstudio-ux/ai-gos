"""
Projects Domain Application Service.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from core.exceptions import NotFoundError, TenantIsolationError
from core.pagination import OffsetPage, PaginationParams
from core.result import Err, Ok, Result
from events.event_bus import EventBus
from events.event_schema import ProjectCreated, ProjectDeleted

from domains.projects.domain.entities.project import BrandVoice, CMSConfig, Project, SEOStrategy
from domains.projects.infrastructure.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class CreateProjectCommand:
    org_id: uuid.UUID
    name: str
    website_url: str
    brand_voice: BrandVoice | None = None
    seo_strategy: SEOStrategy | None = None
    cms_config: CMSConfig | None = None


@dataclass(frozen=True)
class UpdateProjectCommand:
    project_id: uuid.UUID
    org_id: uuid.UUID
    name: str | None = None
    website_url: str | None = None
    brand_voice: BrandVoice | None = None
    seo_strategy: SEOStrategy | None = None
    cms_config: CMSConfig | None = None


class ProjectService:
    """Application service managing SaaS project profiles."""

    def __init__(self, repo: ProjectRepository, event_bus: EventBus | None = None) -> None:
        self._repo = repo
        self._event_bus = event_bus

    async def create_project(self, cmd: CreateProjectCommand) -> Result[Project, Exception]:
        project = Project(
            org_id=cmd.org_id,
            name=cmd.name,
            website_url=cmd.website_url,
            brand_voice=cmd.brand_voice or BrandVoice(),
            seo_strategy=cmd.seo_strategy or SEOStrategy(),
            cms_config=cmd.cms_config or CMSConfig(),
        )
        saved = await self._repo.save(project)

        if self._event_bus:
            await self._event_bus.publish(
                ProjectCreated(
                    aggregate_id=saved.id,
                    org_id=saved.org_id,
                    project_id=saved.id,
                    payload={"name": saved.name, "website_url": saved.website_url},
                )
            )

        return Ok(saved)

    async def get_project(self, project_id: uuid.UUID, org_id: uuid.UUID) -> Result[Project, Exception]:
        project = await self._repo.get_by_id(project_id)
        if not project:
            return Err(NotFoundError("Project not found."))
        if project.org_id != org_id:
            return Err(TenantIsolationError("Cross-tenant access denied."))
        return Ok(project)

    async def list_projects(
        self, org_id: uuid.UUID, params: PaginationParams
    ) -> Result[OffsetPage[Project], Exception]:
        page = await self._repo.list_by_org(org_id, params)
        return Ok(page)

    async def update_project(self, cmd: UpdateProjectCommand) -> Result[Project, Exception]:
        get_res = await self.get_project(cmd.project_id, cmd.org_id)
        if get_res.is_err():
            return get_res

        project = get_res.unwrap()
        updates = {}
        if cmd.name is not None:
            updates["name"] = cmd.name
        if cmd.website_url is not None:
            updates["website_url"] = cmd.website_url
        if cmd.brand_voice is not None:
            updates["brand_voice"] = cmd.brand_voice
        if cmd.seo_strategy is not None:
            updates["seo_strategy"] = cmd.seo_strategy
        if cmd.cms_config is not None:
            updates["cms_config"] = cmd.cms_config

        updated = project.with_update(**updates)
        saved = await self._repo.save(updated)
        return Ok(saved)

    async def delete_project(self, project_id: uuid.UUID, org_id: uuid.UUID) -> Result[bool, Exception]:
        get_res = await self.get_project(project_id, org_id)
        if get_res.is_err():
            return get_res

        deleted = await self._repo.delete(project_id)
        if deleted and self._event_bus:
            await self._event_bus.publish(
                ProjectDeleted(
                    aggregate_id=project_id,
                    org_id=org_id,
                    project_id=project_id,
                )
            )
        return Ok(deleted)
