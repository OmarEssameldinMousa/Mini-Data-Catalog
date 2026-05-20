from sqlalchemy import Column, DateTime, func, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from datetime import datetime
import uuid


class LineageEdge(Base):
    __tablename__ = "lineage_edges"

    upstream_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    downstream_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
