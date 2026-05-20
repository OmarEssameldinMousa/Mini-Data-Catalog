from app.models.basemodel import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid
from sqlalchemy import String, ForeignKey, JSON, Boolean, func, DateTime
from app.models.db_enums.enums import TableNamesEnum
from typing import Optional, List
import uuid
from datetime import datetime
class SchemaVersion(Base):
    __tablename__ = TableNamesEnum.SCHEMA_VERSIONS.value

    id: Mapped[uuid.UUID] = mapped_column(Uuid,primary_key=True, default=uuid.uuid4)
    schema_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(f"{TableNamesEnum.SCHEMAS.value}.id", ondelete="CASCADE"))
    version_number: Mapped[str] = mapped_column(String, default="v1")
    field_definitions: Mapped[dict] = mapped_column(JSON)
    is_current: Mapped[bool] = mapped_column(Boolean)
    is_breaking:  Mapped[bool] = mapped_column(Boolean)
    changelog: Mapped[str] = mapped_column(String) 
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    schema: Mapped["Schema"] = relationship(back_populates="versions")
    validationresult: Mapped["ValidationResult"] = relationship(back_populates="schemaversion", cascade="all, delete-orphan")
    
    