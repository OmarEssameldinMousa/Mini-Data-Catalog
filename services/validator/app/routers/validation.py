from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict, Any
from app.core.database import get_db
from app.repositories.schema_repo import SchemaRepository
from app.services.schema_service import SchemaService
from app.schemas.validation import ValidationContractResponse, ValidationInternalResponse
import uuid

router = APIRouter(
    prefix="/validation",
    tags=["Validation"]
)


def get_schema_service(db: AsyncSession = Depends(get_db)) -> SchemaService:
    repo = SchemaRepository(db)
    return SchemaService(repo)


@router.post("/{schema_id}/validate", response_model=ValidationInternalResponse)
async def validate_payload(
        schema_id: uuid.UUID,
        payload: Dict[str, Any] = Body(...),
        service: SchemaService = Depends(get_schema_service)
):
    """
    Internal validation endpoint. Returns the full response including
    the persisted validation_result_id.
    """
    report, validation_result = await service.validate_payload(schema_id, payload)

    return ValidationInternalResponse(
        valid=report.valid,
        error_count=report.error_count,
        errors=report.errors,
        validation_result_id=validation_result.id
    )


@router.post("/{schema_id}/validate/contract", response_model=ValidationContractResponse)
async def validate_payload_contract(
        schema_id: uuid.UUID,
        payload: Dict[str, Any] = Body(...),
        service: SchemaService = Depends(get_schema_service)
):
    """
    Inter-service contract endpoint for Registry and other services.
    Returns a clean, minimal response — no internal IDs.
    """
    report, _ = await service.validate_payload(schema_id, payload)

    return ValidationContractResponse(
        valid=report.valid,
        error_count=report.error_count,
        errors=report.errors
    )
