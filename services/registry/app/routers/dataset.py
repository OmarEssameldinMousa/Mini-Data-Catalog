# services/registry/app/routers/dataset.py
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from app.schemas.version import DataSetVersionCreate, DataSetVersionRead
from app.services.dataset import DatasetService
from app.models.db_enums.enums import DataFormatEnum, StatusEnum
from app.exceptions import DatasetNotFound, VersionNotFound

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"]
)

@router.get("/search", response_model=List[DatasetRead])
async def search_datasets(
    q: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db)
):
    # TODO: Implement search_datasets in DatasetService / Repository
    raise HTTPException(status_code=501, detail="Search not implemented yet")
    
@router.post("/", response_model=DatasetRead, status_code=201)
async def create_dataset(
    dataset_in: DatasetCreate,
    db: AsyncSession = Depends(get_db)
):
    service = DatasetService(session=db)
    new_dataset = await service.create_dataset(dataset_in=dataset_in)
    return new_dataset
    
@router.get("/", response_model=List[DatasetRead], status_code=200)
async def list_datasets(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, ge=0, le=100),
    offset: int = Query(0, ge=0),
    owner: Optional[str] = None,
    data_format: Optional[DataFormatEnum] = None,
):
    service = DatasetService(session=db)
    
    datasets, total_count = await service.get_datasets(limit=limit, offset=offset, owner=owner, data_format=data_format)
    
    # Returning datasets to match response_model=List[DatasetRead]
    return datasets

@router.get("/{dataset_id}", response_model=DatasetRead)
async def get_dataset(
    dataset_id: str,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    service = DatasetService(session=db)
    dataset = await service.get_dataset(dataset_id)
    
    response.headers["Cache-Control"] = "public, max-age=60"
    if hasattr(dataset, "updated_at") and dataset.updated_at:
        response.headers["ETag"] = f'W/"{dataset.updated_at.timestamp()}"'

    return dataset
    
@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db)
):
    service = DatasetService(session=db)
    await service.soft_delete_dataset(dataset_id)

@router.put("/{dataset_id}", response_model=DatasetRead)
async def update_dataset(
    dataset_id: str,
    dataset_in: DatasetUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = DatasetService(session=db)
    updated_dataset = await service.update_dataset(dataset_id, dataset_in)
    return updated_dataset    

from app.clients.validator_client import ValidatorClient

# Add a new version with schema snapshot       
@router.post("/{dataset_id}/versions", response_model=DataSetVersionRead, status_code=201)
async def add_dataset_version(
    request: Request,
    dataset_id: str,
    version_data: DataSetVersionCreate,
    db: AsyncSession = Depends(get_db),
):
    service = DatasetService(session=db)
    
    validator_client = ValidatorClient(
        http_client=request.app.state.http_client,
        base_url=request.app.state.validator_url
    )
    
    new_version = await service.create_dataset_version(dataset_id, version_data, validator_client=validator_client)
    return new_version

# list all versions of a dataset
@router.get("/{dataset_id}/versions", response_model=List[DataSetVersionRead])
async def list_dataset_versions(
    dataset_id: str,
    limit: int = Query(20, ge=0, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    service = DatasetService(session=db)
    versions, total = await service.get_dataset_versions(dataset_id, limit, offset)
    return versions

