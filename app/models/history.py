"""Search and export history models."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SearchHistoryEntity(Base):
    """Persisted search execution metadata."""

    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(100), index=True)
    query: Mapped[str] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_count: Mapped[int] = mapped_column(Integer)
    discovered_count: Mapped[int] = mapped_column(Integer)
    output_file: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))


class ExportHistoryEntity(Base):
    """Persisted export history for auditability."""

    __tablename__ = "export_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    export_type: Mapped[str] = mapped_column(String(60), index=True)
    target: Mapped[str] = mapped_column(String(1024))
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(tz=UTC))
