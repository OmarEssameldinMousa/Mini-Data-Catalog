from app.models.basemodel import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
from sqlalchemy import String, ForeignKey, JSON, Boolean, func, DateTime, UniqueConstraint
from app.models.db_enums.enums import TableNamesEnum
from typing import Optional, List
import uuid
from datetime import datetime


class ValidationResult(Base):
    __tablename__ = TableNamesEnum.VALIDATION_RESULTS.value

    __table_args__ = (
        UniqueConstraint("schema_version_id", "payload_hash", name="uq_version_payload"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    schema_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNamesEnum.SCHEMA_VERSIONS.value}.id", ondelete="cascade"), nullable=False)
    
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean)
    error_report: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    schemaversion: Mapped["SchemaVersion"] = relationship("SchemaVersion", back_populates="validationresult")