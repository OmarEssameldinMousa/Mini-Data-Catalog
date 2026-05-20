from pydantic import BaseModel, computed_field, ConfigDict
from typing import Optional, List, Any
import uuid

class FieldError(BaseModel):
    field: str
    code: str 
    message: str
    received: Optional[Any] = None 
    expected: Optional[Any] = None 

class ValidationReport(BaseModel):
    valid: bool
    errors: List[FieldError]

    @computed_field
    @property
    def error_count(self)-> int:
        return len(self.errors)


class ValidationContractResponse(BaseModel):
    """
    Inter-service contract response for Registry and other services.
    Clean, minimal shape — no internal IDs exposed.
    Field name 'valid' matches ValidationReport.valid for consistency.
    """
    valid: bool
    error_count: int
    errors: List[FieldError]


class ValidationInternalResponse(BaseModel):
    """
    Internal response that includes the persisted validation_result_id.
    Used by the Validator's own API consumers.
    """
    valid: bool
    error_count: int
    errors: List[FieldError]
    validation_result_id: uuid.UUID
