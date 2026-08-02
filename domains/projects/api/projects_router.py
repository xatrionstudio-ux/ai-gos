"""
FastAPI router for Projects endpoints.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.pagination import OffsetPage, PaginationParams
from core.result import Err, Ok
from domains.identity.api.dependencies import get_current_user, get_db_session, require_permission
from domains.identity.domain.entities.user import Permission, User
from domains.projects.application.project_service import (
    CreateProjectCommand,
    ProjectService,
    UpdateProjectCommand,
)
from domains.projects.domain.entities.project import BrandVoice, CMSConfig, Project, SEOStrategy
from domains.projects.infrastructure.repositories.project_repository import ProjectRepository

router = APIRouter(prefix="/v1/projects", tags=["Projects"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    website_url: str = Field(..., min_length=4)
    brand_voice: BrandVoice | None = None
    seo_strategy: SEOStrategy | None = None
    cms_config: CMSConfig | None = None


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    website_url: str | None = Field(default=None, min_length=4)
    brand_voice: BrandVoice | None = None
    seo_strategy: SEOStrategy | None = None
    cms_config: CMSConfig | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    website_url: str
    brand_voice: BrandVoice
    seo_strategy: SEOStrategy
    cms_config: CMSConfig
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, p: Project) -> "ProjectResponse":
        return cls(
            id=p.id,
            org_id=p.org_id,
            name=p.name,
            website_url=p.website_url,
            brand_voice=p.brand_voice,
            seo_strategy=p.seo_strategy,
            cms_config=p.cms_config,
            status=p.status,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )


ProjectResponse.model_rebuild()


async def get_project_service(session: AsyncSession = Depends(get_db_session)) -> ProjectService:
    repo = ProjectRepository(session)
    return ProjectService(repo)


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new SaaS project profile",
)
async def create_project(
    req: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.PROJECTS_WRITE)),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    cmd = CreateProjectCommand(
        org_id=current_user.org_id,
        name=req.name,
        website_url=req.website_url,
        brand_voice=req.brand_voice,
        seo_strategy=req.seo_strategy,
        cms_config=req.cms_config,
    )
    res = await service.create_project(cmd)
    if res.is_ok():
        return ProjectResponse.from_entity(res.value)
    else:
        raise HTTPException(status_code=400, detail=str(res.error))


@router.get(
    "",
    response_model=OffsetPage[ProjectResponse],
    summary="List projects for the user's organization",
)
async def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.PROJECTS_READ)),
    service: ProjectService = Depends(get_project_service),
) -> OffsetPage[ProjectResponse]:
    params = PaginationParams(page=page, size=size)
    res = await service.list_projects(current_user.org_id, params)
    if res.is_ok():
        items = [ProjectResponse.from_entity(p) for p in res.value.items]
        return OffsetPage.create(items=items, total=res.value.total, params=params)
    else:
        raise HTTPException(status_code=400, detail=str(res.error))


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.PROJECTS_READ)),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    res = await service.get_project(project_id, current_user.org_id)
    if res.is_ok():
        return ProjectResponse.from_entity(res.value)
    else:
        raise HTTPException(status_code=404, detail=str(res.error))


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project profile",
)
async def update_project(
    project_id: uuid.UUID,
    req: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.PROJECTS_WRITE)),
    service: ProjectService = Depends(get_project_service),
) -> ProjectResponse:
    cmd = UpdateProjectCommand(
        project_id=project_id,
        org_id=current_user.org_id,
        name=req.name,
        website_url=req.website_url,
        brand_voice=req.brand_voice,
        seo_strategy=req.seo_strategy,
        cms_config=req.cms_config,
    )
    res = await service.update_project(cmd)
    if res.is_ok():
        return ProjectResponse.from_entity(res.value)
    else:
        raise HTTPException(status_code=400, detail=str(res.error))


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete a project profile",
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.PROJECTS_DELETE)),
    service: ProjectService = Depends(get_project_service),
) -> None:
    res = await service.delete_project(project_id, current_user.org_id)
    if res.is_err():
        raise HTTPException(status_code=400, detail=str(res.error))
