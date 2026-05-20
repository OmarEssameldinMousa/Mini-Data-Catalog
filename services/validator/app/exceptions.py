# app/exceptions.py
"""
Domain exceptions for the Validator service.
Mirrors the pattern used in Registry (registry/app/exceptions.py).
These are caught by exception handlers registered in main.py,
keeping route handlers free of try/except blocks.
"""


class ValidatorException(Exception):
    """Base class for all Validator service exceptions."""
    pass


class SchemaNotFound(ValidatorException):
    """
    Raised when a schema ID does not exist.
    Caught by an exception handler and returned as HTTP 404.
    """

    def __init__(self, schema_id: str):
        self.schema_id = schema_id
        super().__init__(f"Schema '{schema_id}' not found.")


class SchemaVersionNotFound(ValidatorException):
    """
    Raised when a specific schema version does not exist.
    Caught by an exception handler and returned as HTTP 404.
    """

    def __init__(self, schema_id: str, version_number: str):
        self.schema_id = schema_id
        self.version_number = version_number
        super().__init__(
            f"Version '{version_number}' not found for schema '{schema_id}'."
        )


class ActiveVersionNotFound(ValidatorException):
    """
    Raised when no active (is_current=True) version exists for a schema.
    Caught by an exception handler and returned as HTTP 404.
    """

    def __init__(self, schema_id: str):
        self.schema_id = schema_id
        super().__init__(
            f"No active version found for schema '{schema_id}'."
        )
