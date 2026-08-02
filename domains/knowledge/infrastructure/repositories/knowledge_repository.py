"""
SQLAlchemy repository implementation for KnowledgeRepository.
"""

from __future__ import annotations

import uuid
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.pagination import OffsetPage, PaginationParams
from domains.knowledge.domain.entities.knowledge import (
    DocumentType,
    EntityType,
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeEntity,
    KnowledgeSource,
)
from domains.knowledge.infrastructure.models.orm_models import (
    KnowledgeChunkModel,
    KnowledgeDocumentModel,
    KnowledgeEntityModel,
    KnowledgeSourceModel,
)


class KnowledgeRepository:
    """Async repository for Knowledge Documents, Chunks, and Entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ─── Documents ─────────────────────────────────────────────────────────────

    def _to_doc_entity(self, model: KnowledgeDocumentModel) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=model.id,
            project_id=model.project_id,
            source_id=model.source_id,
            title=model.title,
            content=model.content,
            content_hash=model.content_hash,
            document_type=DocumentType(model.document_type),
            metadata=model.metadata,
            version=model.version,
            is_current=model.is_current,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def save_document(self, doc: KnowledgeDocument) -> KnowledgeDocument:
        stmt = select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.id == doc.id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()

        if not model:
            model = KnowledgeDocumentModel(
                id=doc.id,
                project_id=doc.project_id,
                source_id=doc.source_id,
                title=doc.title,
                content=doc.content,
                content_hash=doc.content_hash,
                document_type=doc.document_type.value,
                metadata=doc.metadata,
                version=doc.version,
                is_current=doc.is_current,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            self._session.add(model)
        else:
            model.title = doc.title
            model.content = doc.content
            model.content_hash = doc.content_hash
            model.document_type = doc.document_type.value
            model.metadata = doc.metadata
            model.version = doc.version
            model.is_current = doc.is_current
            model.updated_at = doc.updated_at

        await self._session.flush()
        return self._to_doc_entity(model)

    async def list_documents_by_project(
        self, project_id: uuid.UUID, params: PaginationParams
    ) -> OffsetPage[KnowledgeDocument]:
        stmt = (
            select(KnowledgeDocumentModel)
            .where(KnowledgeDocumentModel.project_id == project_id)
            .offset(params.offset)
            .limit(params.size)
        )
        res = await self._session.execute(stmt)
        models = res.scalars().all()

        count_stmt = select(KnowledgeDocumentModel).where(KnowledgeDocumentModel.project_id == project_id)
        count_res = await self._session.execute(count_stmt)
        total = len(count_res.scalars().all())

        items = [self._to_doc_entity(m) for m in models]
        return OffsetPage.create(items=items, total=total, params=params)

    # ─── Entities ──────────────────────────────────────────────────────────────

    def _to_entity(self, model: KnowledgeEntityModel) -> KnowledgeEntity:
        return KnowledgeEntity(
            id=model.id,
            project_id=model.project_id,
            entity_type=EntityType(model.entity_type),
            name=model.name,
            description=model.description,
            attributes=model.attributes,
            source_document_ids=model.source_document_ids or [],
            confidence=model.confidence,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def save_entity(self, entity: KnowledgeEntity) -> KnowledgeEntity:
        stmt = select(KnowledgeEntityModel).where(KnowledgeEntityModel.id == entity.id)
        res = await self._session.execute(stmt)
        model = res.scalar_one_or_none()

        if not model:
            model = KnowledgeEntityModel(
                id=entity.id,
                project_id=entity.project_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                description=entity.description,
                attributes=entity.attributes,
                source_document_ids=entity.source_document_ids,
                confidence=entity.confidence,
                created_at=entity.created_at,
                updated_at=entity.updated_at,
            )
            self._session.add(model)
        else:
            model.name = entity.name
            model.description = entity.description
            model.attributes = entity.attributes
            model.source_document_ids = entity.source_document_ids
            model.confidence = entity.confidence
            model.updated_at = entity.updated_at

        await self._session.flush()
        return self._to_entity(model)

    async def list_entities_by_project(
        self, project_id: uuid.UUID
    ) -> list[KnowledgeEntity]:
        stmt = select(KnowledgeEntityModel).where(KnowledgeEntityModel.project_id == project_id)
        res = await self._session.execute(stmt)
        models = res.scalars().all()
        return [self._to_entity(m) for m in models]
