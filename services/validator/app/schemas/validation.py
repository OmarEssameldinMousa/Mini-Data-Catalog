from pydantic import BaseModel, computed_field
from typing import Optional, List, Any

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
