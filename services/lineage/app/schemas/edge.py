import uuid
from pydantic import model_validator, BaseModel, Field,  ConfigDict

from datetime import datetime

class EdgeCreate(BaseModel):
    upstream_id: uuid.UUID = Field(..., description="ID of the upstream dataset")
    downstream_id: uuid.UUID = Field(..., description="ID of the downstream dataset")

    @model_validator(mode="before")
    def validate_ids(cls, values):
        if values["upstream_id"] == values["downstream_id"]:
            raise ValueError("upstream_id and downstream_id cannot be the same")
        return values

class EdgeResponse(BaseModel):
    upstream_id: uuid.UUID
    downstream_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)