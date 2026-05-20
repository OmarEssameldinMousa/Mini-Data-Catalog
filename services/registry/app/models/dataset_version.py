from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON, BigInteger, func
from datetime import datetime
from .basemodel import Base

import uuid
from sqlalchemy.types import Uuid

class DatasetVersion(Base):
    __tablename__ = "dataset_version"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("dataset.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(nullable=False, default=1)
    schema_snapshot: Mapped[dict] = mapped_column(JSON) 
    row_count: Mapped[int] = mapped_column(BigInteger)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="versions")
