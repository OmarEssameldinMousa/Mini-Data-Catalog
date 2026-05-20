"""
Domain exceptions for the Lineage service.
Caught by exception handlers registered in main.py.
"""


class LineageException(Exception):
    """Base class for all Lineage service exceptions."""
    pass


class EdgeNotFound(LineageException):
    """Raised when an edge does not exist."""

    def __init__(self, upstream_id: str, downstream_id: str):
        self.upstream_id = upstream_id
        self.downstream_id = downstream_id
        super().__init__(
            f"Edge from '{upstream_id}' to '{downstream_id}' not found."
        )


class EdgeAlreadyExists(LineageException):
    """Raised when trying to create a duplicate edge."""

    def __init__(self, upstream_id: str, downstream_id: str):
        self.upstream_id = upstream_id
        self.downstream_id = downstream_id
        super().__init__(
            f"Edge from '{upstream_id}' to '{downstream_id}' already exists."
        )


class DatasetNotFoundInRegistry(LineageException):
    """Raised when a dataset ID is not found in the Registry service."""

    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__(
            f"Dataset '{dataset_id}' not found in Registry."
        )


class CycleDetected(LineageException):
    """Raised when creating an edge would introduce a cycle."""

    def __init__(self, upstream_id: str, downstream_id: str):
        self.upstream_id = upstream_id
        self.downstream_id = downstream_id
        super().__init__(
            f"Creating edge from '{upstream_id}' to '{downstream_id}' would introduce a cycle."
        )


class ServiceUnavailableError(LineageException):
    """Raised when Registry service is unreachable."""

    def __init__(self, service_name: str, detail: str = ""):
        self.service_name = service_name
        super().__init__(
            f"Service '{service_name}' is unavailable. {detail}"
        )
