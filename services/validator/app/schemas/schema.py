from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from app.schemas.field import FieldDefinition
import uuid 
from datetime import datetime

class SchemaCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str
    initial_fields: List[FieldDefinition]

class SchemaResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    owner: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VersionCreateRequest(BaseModel):
    fields: List[FieldDefinition]
    version_number: str

