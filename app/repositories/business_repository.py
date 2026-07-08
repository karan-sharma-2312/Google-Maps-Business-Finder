"""Repository for business entities."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business import BusinessEntity
from app.schemas.business import BusinessRecord, Coordinates


class BusinessRepository:
    """Data access for discovered businesses."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_many(self, records: list[BusinessRecord]) -> list[BusinessEntity]:
        """Insert or update business records by Google Maps URL."""
        entities: list[BusinessEntity] = []
        for record in records:
            existing = None
            if record.google_maps_url:
                stmt = select(BusinessEntity).where(BusinessEntity.google_maps_url == str(record.google_maps_url))
                existing = await self._session.scalar(stmt)

            entity = existing or BusinessEntity()
            entity.business_name = record.business_name
            entity.category = record.category
            entity.rating = record.rating
            entity.reviews_count = record.reviews_count
            entity.address = record.address
            entity.phone = record.phone
            entity.website = str(record.website) if record.website else None
            entity.google_maps_url = str(record.google_maps_url) if record.google_maps_url else None
            entity.latitude = record.coordinates.latitude
            entity.longitude = record.coordinates.longitude
            entity.opening_hours_json = json.dumps(record.opening_hours, ensure_ascii=True)
            entity.business_status = record.business_status
            entity.business_description = record.business_description
            entity.business_images_json = json.dumps([str(url) for url in record.business_images], ensure_ascii=True)

            if existing is None:
                self._session.add(entity)
            entities.append(entity)

        await self._session.commit()
        return entities

    async def list_recent(self, limit: int = 50) -> list[BusinessRecord]:
        """Return most recent persisted businesses."""
        stmt = select(BusinessEntity).order_by(BusinessEntity.id.desc()).limit(limit)
        rows = (await self._session.scalars(stmt)).all()
        output: list[BusinessRecord] = []
        for row in rows:
            output.append(
                BusinessRecord(
                    business_name=row.business_name,
                    category=row.category,
                    rating=row.rating,
                    reviews_count=row.reviews_count,
                    address=row.address,
                    phone=row.phone,
                    website=row.website,
                    google_maps_url=row.google_maps_url,
                    coordinates=Coordinates(latitude=row.latitude, longitude=row.longitude),
                    opening_hours=json.loads(row.opening_hours_json) if row.opening_hours_json else [],
                    business_status=row.business_status,
                    business_description=row.business_description,
                    business_images=json.loads(row.business_images_json) if row.business_images_json else [],
                )
            )
        return output
