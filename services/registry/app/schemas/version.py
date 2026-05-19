from pydantic import BaseModel, ConfigDict
from datetime import datetime

class DataSetVersionBase(BaseModel):
    dataset_id: int 
    version_number: int
    schema_snapshot: dict
    row_count: int
    file_size_bytes: int

class DataSetVersionCreate(BaseModel):
    schema_snapshot: dict
    row_count: int
    file_size_bytes: int

class DataSetVersionRead(DataSetVersionBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)