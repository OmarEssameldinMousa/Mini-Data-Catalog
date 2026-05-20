from pydantic import ConfigDict, BaseModel
import uuid
from datetime import datetime


class DatasetDepthResponse(BaseModel):
    dataset_id: uuid.UUID
    depth: int


class LineageGraphResponse(BaseModel):
    upstream: list[uuid.UUID]
    downstream: list[uuid.UUID]