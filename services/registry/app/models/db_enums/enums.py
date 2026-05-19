
import enum

class DataFormatEnum(enum.Enum):
    CSV= "csv"
    PARQUET= "parquet"
    DELTA= "delta"
    JSON= "json"

class StatusEnum(enum.Enum):
    ACTIVE= "active"
    DEPRECATED= "deprecated"
    DRAFT= "draft"
