from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid
from sqlalchemy import String, Integer, JSON, DateTime, func
from app.models.base import Base
from typing import Optional
import uuid
from datetime import datetime


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    schema_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    dataset_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    row_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    inferred_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
