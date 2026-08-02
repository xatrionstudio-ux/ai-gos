"""
SQLAlchemy repository implementation for ProjectRepository.
"""

from __future__ import annotations

import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_repository import BaseRepository
from core.pagination import OffsetPage, PaginationParams
from domains.projects.domain.entities.project import BrandVoice, CMSConfig, Project, SEOStrategy
from domains.projects.infrastructure.models.orm_models import ProjectModel


class ProjectRepository(BaseRepository[Project]):
    """Async SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            org_id=model.org_id,
            name=model.name,
            website_url=model.website_url,
            brand_voice=BrandVoice.model_validate(model.brand_voice or {}),
            seo_strategy=SEOStrategy.model_validate(model.seo_strategy or {}),
            cms_config=CMSConfig.model_validate(model.cms_config or {}),
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_id(self, entity_id: uuid.UUID) -> Project | None:
        stmt = select(ProjectModel).where(ProjectModel.id == entity_id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, entity: Project) -> Project:
        stmt = select(ProjectModel).where(ProjectModel.id == entity.id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()

        if not model:
            model = ProjectModel(
                id=entity.id,
                org_id=entity.org_id,
                name=entity.name,
                website_url=entity.website_url,
                brand_voice=entity.brand_voice.model_dump(),
                seo_strategy=entity.seo_strategy.model_dump(),
                cms_config=entity.cms_config.model_dump(),
                status=entity.status,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            self._session.add(model)
        else:
            model.name = entity.name
            model.website_url = entity.website_url
            model.brand_voice = entity.brand_voice.model_dump()
            model.seo_strategy = entity.seo_strategy.model_dump()
            model.cms_config = entity.cms_config.model_dump()
            model.status = entity.status
            model.updated_at = entity.updated_at

        await self._session.flush()
        return self._to_entity(model)

    async def delete(self, entity_id: uuid.UUID) -> bool:
        stmt = delete(ProjectModel).where(ProjectModel.id == entity_id)
        res = await self._session.execute(stmt)
        return res.rowcount > 0

    async def list_by_org(
        self, org_id: uuid.UUID, params: PaginationParams
    ) -> OffsetPage[Project]:
        stmt = (
            select(ProjectModel)
            .where(ProjectModel.org_id == org_id)
            .offset(params.offset)
            .limit(params.size)
        )
        res = await self._session.execute(stmt)
        models = res.scalars().all()

        count_stmt = select(ProjectModel).where(ProjectModel.org_id == org_id)
        count_res = await self._session.execute(count_stmt)
        total = len(count_res.scalars().all())

        items = [self._to_entity(m) for m in models]
        return OffsetPage.create(items=items, total=total, params=params)

    async def list(self, params: PaginationParams) -> OffsetPage[Project]:
        stmt = select(ProjectModel).offset(params.offset).limit(params.size)
        res = await self._session.execute(stmt)
        models = res.scalars().all()

        items = [self._to_entity(m) for m in models]
        return OffsetPage.create(items=items, total=len(items), params=params)

    async def exists(self, entity_id: uuid.UUID) -> bool:
        stmt = select(ProjectModel.id).where(ProjectModel.id == entity_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() is not None
