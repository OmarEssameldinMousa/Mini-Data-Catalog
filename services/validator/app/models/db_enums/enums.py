import enum


class TableNamesEnum(enum.Enum):
    SCHEMAS = "schemas"
    SCHEMA_VERSIONS = "schema_versions"
    VALIDATION_RESULTS = "validation_results"

class ErrorCodesEnum(enum.Enum):
    FIELD_MISSING = "FIELD_MISSING"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    FIELD_UNKNOWN = "FIELD_UNKNOWN"
    NULL_VIOLATION = "NULL_VIOLATION"