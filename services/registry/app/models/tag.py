from .basemodel import Base
from sqlalchemy.orm import Mapped, relationship, mapped_column
from typing import List
class Tag(Base):
    __tablename__ = "tag"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    
    datasets: Mapped[List["Dataset"]] = relationship(
        secondary="dataset_tag_association",
        back_populates="tags"
    )
