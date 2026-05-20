import httpx
import uuid
from typing import Dict, Any, Optional


class SchemaValidationError(Exception):
    pass


class SchemaValidatorClient:
    """
    Async HTTP client for the Validator service.
    Uses the /validate/contract endpoint for clean inter-service responses.
    """

    def __init__(self, http_client: httpx.AsyncClient, base_url: str):
        self.http_client = http_client
        self.base_url = base_url

    async def validate_row(self, schema_id: uuid.UUID, payload: Dict[str, Any]) -> bool:
        """
        Validate a single row against a schema via Validator's contract endpoint.
        Returns True if valid, raises SchemaValidationError if invalid or not found.
        """
        response = await self.http_client.post(
            f"{self.base_url}/validation/{schema_id}/validate/contract",
            json=payload,
            timeout=10.0
        )

        if response.status_code == 404:
            raise SchemaValidationError(f"Schema with ID {schema_id} not found.")

        response.raise_for_status()

        data = response.json()
        if not data.get("valid"):
            raise SchemaValidationError(f"Validation failed: {data.get('errors', [])}")

        return True