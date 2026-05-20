# services/registry/app/schemas/dataset.py
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime

from app.models.db_enums.enums import DataFormatEnum, StatusEnum

from app.schemas.tag import TagRead
from app.schemas.version import DataSetVersionRead, DataSetVersionCreate

class DatasetBase(BaseModel):
    name: str = Field(..., max_length=50)
    owner: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    source_uri: str = Field(..., max_length=255)
    data_format: DataFormatEnum

class DatasetCreate(DatasetBase):    
    tags: Optional[List[str]] = []
    versions: List[DataSetVersionCreate] 

class DatasetUpdate(BaseModel):
    name: Optional[str] = None
    owner: Optional[str] = None
    description: Optional[str] = None
    source_uri: Optional[str] = None
    data_format: Optional[DataFormatEnum] = None
    status: Optional[StatusEnum] = None
    
    tags: Optional[List[str]] = None

import uuid

class DatasetRead(DatasetBase):
    
    id: uuid.UUID 
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    tags: List[TagRead] = []
    versions: List[DataSetVersionRead] = []
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedDatasetResponse(BaseModel):
    total: int
    page: int
    size: int
    items: List[DatasetRead]