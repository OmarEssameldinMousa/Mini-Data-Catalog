from app.models.basemodel import Base
from app.models.db_enums.enums import TableNamesEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, JSON, BigInteger, DateTime, func
from sqlalchemy.types import Uuid
from typing import List 
from datetime import datetime
import uuid 

class Schema(Base):
    __tablename__ = TableNamesEnum.SCHEMAS.value

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255))
    owner: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    versions: Mapped[List["SchemaVersion"]] = relationship("SchemaVersion", back_populates="schema", cascade="all, delete-orphan")
    
    