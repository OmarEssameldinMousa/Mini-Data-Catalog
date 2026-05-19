from .basemodel import Base
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import String, ForeignKey, func, Table, Column, Index
from typing import Optional, List
from .db_enums.enums import StatusEnum, DataFormatEnum
from datetime import datetime

dataset_tag_association = Table(
    "dataset_tag_association",
    Base.metadata,
    Column("dataset_id", ForeignKey("dataset.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
)

class Dataset(Base):
    __tablename__ = "dataset"

    __table_args__ = (
        Index("idx_dataset_owner_data_format", "owner", "data_format"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    owner: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(500), nullable=True) # Assuming nullable here
    source_uri: Mapped[str] = mapped_column(String(255))
    
    data_format: Mapped[DataFormatEnum] = mapped_column(nullable=False)
    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.ACTIVE, nullable=False)                                                                            
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())                                                                
    
    versions: Mapped[List["DatasetVersion"]] = relationship(
        back_populates="dataset", 
        cascade="all, delete-orphan"
    )

    tags: Mapped[List["Tag"]] = relationship(
        secondary="dataset_tag_association",
        back_populates="datasets"
    )

