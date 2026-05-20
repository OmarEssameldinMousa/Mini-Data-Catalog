import httpx
import uuid
from app.exceptions import SchemaValidationFailed, ServiceUnavailableError

class ValidatorClient:
    def __init__(self, http_client: httpx.AsyncClient, base_url: str):
        self.http_client = http_client
        self.base_url = base_url

    async def validate(self, schema_id: uuid.UUID, payload: dict) -> None:
        """
        Calls POST /validation/{schema_id}/validate/contract
        Raises SchemaValidationFailed if valid=False.
        Raises ServiceUnavailableError on connection issues.
        Returns None on success — caller just continues.
        """
        try:
            response = await self.http_client.post(
                f"{self.base_url}/validation/{schema_id}/validate/contract",
                json=payload,
                timeout=httpx.Timeout(connect=3.0, read=10.0, write=5.0, pool=2.0),
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("valid"):
                raise SchemaValidationFailed(errors=data.get("errors", []))
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SchemaValidationFailed(errors=[{"message": "Validator schema not found."}])
            raise ServiceUnavailableError(service_name="Validator", detail=str(e))
        except httpx.ConnectError:
            raise ServiceUnavailableError(service_name="Validator")
        except httpx.TimeoutException:
            raise ServiceUnavailableError(service_name="Validator", detail="timeout")
