from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Dict, Any
from app.core.database import get_db
from app.repositories.schema_repo import SchemaRepository
from app.services.validation_engine import ValidationEngine
from app.schemas.field import FieldDefinition
import uuid
import hashlib
import json

router = APIRouter(
    prefix="/validation",
    tags=["Validation"]
)


@router.post("/{schema_id}/validate")
async def validate_payload(
        schema_id: uuid.UUID,
        payload: Dict[str, Any] = Body(...),
        db: AsyncSession = Depends(get_db)
):
    
    repo = SchemaRepository(db)
    current_active_version = await repo.get_current_active_schema_version(schema_id)
    if not current_active_version:
        raise HTTPException(status_code=404, detail="Active schema version not found")
    
    parsed_fields = [FieldDefinition.model_validate(f) for f in current_active_version.field_definitions]

    engine = ValidationEngine(fields=parsed_fields)
    
    result = await engine.validate(payload)

    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    validation_result = await repo.save_validation_result(
        schema_version_id=current_active_version.id,
        is_valid=result.valid,
        error_report=result.model_dump(),
        payload_hash=payload_hash
    )   
    # validation report 
    
    return {
        "is_valid": result.valid,
        "error_report": result.model_dump(),
        "validation_result_id": validation_result.id   
    } 


