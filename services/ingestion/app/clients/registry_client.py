import httpx
import uuid
from typing import Dict, Any, Optional


class RegistryClient:
    """
    Async HTTP client for the Registry service.
    Used to register dataset versions after successful CSV processing.
    """

    def __init__(self, http_client: httpx.AsyncClient, base_url: str):
        self.http_client = http_client
        self.base_url = base_url

    async def get_dataset(self, dataset_id: str) -> Optional[dict]:
        """Check if a dataset exists in Registry. Returns the dataset dict or None."""
        response = await self.http_client.get(
            f"{self.base_url}/datasets/{dataset_id}",
            timeout=10.0
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def create_dataset_version(
        self,
        dataset_id: str,
        schema_snapshot: dict,
        row_count: int,
        file_size_bytes: int
    ) -> dict:
        """Create a new version for a dataset in Registry."""
        response = await self.http_client.post(
            f"{self.base_url}/datasets/{dataset_id}/versions",
            json={
                "schema_snapshot": schema_snapshot,
                "row_count": row_count,
                "file_size_bytes": file_size_bytes
            },
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
