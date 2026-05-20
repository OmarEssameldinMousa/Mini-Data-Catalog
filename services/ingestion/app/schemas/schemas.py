import enum
from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    FAILED = "failed"


class JobResponse(BaseModel):
    """Pydantic response model for job status — reads from ORM."""
    id: uuid.UUID
    schema_id: uuid.UUID
    dataset_id: Optional[uuid.UUID] = None
    status: str
    filename: str
    row_count: Optional[int] = None
    inferred_schema: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)