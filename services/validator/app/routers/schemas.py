from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.schema_service import SchemaService
from app.schemas.schema import SchemaCreateRequest, VersionCreateRequest, SchemaResponse
from app.models.db_enums.enums import ErrorCodesEnum
from app.repositories.schema_repo import SchemaRepository
import uuid
router = APIRouter(
    prefix="/schemas",
    tags=["Schemas"]
)

def get_schema_service(db: AsyncSession = Depends(get_db)) -> SchemaService:
    repo = SchemaRepository(db)
    return SchemaService(repo)

@router.post("/", response_model=SchemaResponse)
async def create_schema(
        request: SchemaCreateRequest,
        service: SchemaService = Depends(get_schema_service)
    ):

    new_schema = await service.create_new_schema(
            name=request.name, 
            description=request.description, 
            owner=request.owner, 
            initial_fields=request.initial_fields
        )
    
    return new_schema


@router.post("/{schema_id}/versions/{version_number}")
async def add_schema_version(
    schema_id: uuid.UUID,
    version_number: str,
    request: VersionCreateRequest,
    service: SchemaService = Depends(get_schema_service)
    ):
    try:
        await service.add_schema_version(schema_id=schema_id,new_fields=request.fields, new_version_number=version_number)
        return {
            "message": "Version Created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    


@router.get("/{schema_id}/versions/{version_number}/stats")
async def get_schema_stats(
    schema_id: uuid.UUID, 
    version_number: str,
    service: SchemaService = Depends(get_schema_service)
):
    schema_version = await service.get_schema_with_version(schema_id=schema_id, version_number=version_number)
    
    if not schema_version:
        raise HTTPException(status_code=404, detail="Schema version not found")
    
    stats = await service.get_schema_version_stats(schema_version_id=schema_version.id)
    
    return stats