import httpx
from typing import Optional


class RegistryClient:
    """
    Async HTTP client for the Registry service.
    Used to verify dataset IDs exist before creating lineage edges.
    """

    def __init__(self, http_client: httpx.AsyncClient, base_url: str):
        self.http_client = http_client
        self.base_url = base_url

    async def get_dataset(self, dataset_id: str) -> Optional[dict]:
        """
        Check if a dataset exists in Registry.
        Returns the dataset dict or None if not found.
        Raises httpx.ConnectError / httpx.TimeoutException on connection issues.
        """
        response = await self.http_client.get(
            f"{self.base_url}/datasets/{dataset_id}",
            timeout=10.0,
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
