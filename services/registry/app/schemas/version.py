from pydantic import BaseModel, ConfigDict
from datetime import datetime

import uuid

class DataSetVersionBase(BaseModel):
    dataset_id: uuid.UUID 
    version_number: int
    schema_snapshot: dict
    row_count: int
    file_size_bytes: int

import uuid

class DataSetVersionCreate(BaseModel):
    schema_snapshot: dict
    row_count: int
    file_size_bytes: int
    validator_schema_id: uuid.UUID | None = None

class DataSetVersionRead(DataSetVersionBase):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)