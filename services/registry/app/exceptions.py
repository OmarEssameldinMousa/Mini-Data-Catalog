# app/exceptions.py
class RegistryException(Exception):
    """Base class for all Registry service exceptions."""
    pass

class DatasetNotFound(RegistryException):
    """
    Raised when a dataset ID does not exist.
    Should be caught by an exception handler and returned as HTTP 404.
    Carry the dataset_id so the handler can include it in the response.
    """
    
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__(f"Dataset '{dataset_id}' not found.")

class DatasetAlreadyExists(RegistryException):
    """
    Raised when trying to create a dataset with an ID that already exists.
    Should be caught by an exception handler and returned as HTTP 409.
    Carry the dataset_id so the handler can include it in the response.
    """
    
    def __init__(self, dataset_id: str):
        self.dataset_id = dataset_id
        super().__init__(f"Dataset '{dataset_id}' already exists.")
        
class VersionNotFound(RegistryException):
    def __init__(self, version_id: str):
        self.version_id = version_id
        super().__init__(f"Version '{version_id}' not found.")

class SchemaValidationFailed(RegistryException):
    """
    Raised when validation against a schema fails.
    Should return HTTP 422 with the validation errors.
    """
    def __init__(self, errors: list):
        self.errors = errors
        super().__init__("Schema validation failed.")

class ServiceUnavailableError(RegistryException):
    """Raised when an external service is unreachable."""
    def __init__(self, service_name: str, detail: str = ""):
        self.service_name = service_name
        self.detail = detail
        super().__init__(f"Service '{service_name}' is unavailable. {detail}")
