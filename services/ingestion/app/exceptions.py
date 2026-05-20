"""
Domain exceptions for the Ingestion service.
Caught by exception handlers registered in main.py.
"""


class IngestionException(Exception):
    """Base class for all Ingestion service exceptions."""
    pass


class JobNotFound(IngestionException):
    """Raised when a job ID does not exist."""

    def __init__(self, job_id: str):
        self.job_id = job_id
        super().__init__(f"Job '{job_id}' not found.")
