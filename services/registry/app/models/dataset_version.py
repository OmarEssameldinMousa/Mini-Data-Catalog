from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON, BigInteger, func
from datetime import datetime
from .basemodel import Base

class DatasetVersion(Base):
    __tablename__ = "dataset_version"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("dataset.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(nullable=False, default=1)
    schema_snapshot: Mapped[dict] = mapped_column(JSON) 
    row_count: Mapped[int] = mapped_column(BigInteger)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    dataset: Mapped["Dataset"] = relationship(back_populates="versions")
