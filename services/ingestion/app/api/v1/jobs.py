import asyncio
import tempfile
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    Request,
    status,
    Form,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.repositories.job_repo import JobRepository
from app.clients.validator import SchemaValidatorClient
from app.clients.registry_client import RegistryClient
from app.services.worker import process_csv_task
from app.schemas.schemas import JobResponse
from app.exceptions import JobNotFound

jobs_router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@jobs_router.post("/upload", status_code=status.HTTP_202_ACCEPTED, response_model=JobResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    schema_id: uuid.UUID = Form(...),
    dataset_id: uuid.UUID = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload a CSV for ingestion. Validates against schema, then registers with Registry."""
    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed",
        )

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    file.file.seek(0)
    shutil.copyfileobj(file.file, temp)
    temp.close()

    repo = JobRepository(db)
    job = await repo.create_job(
        filename=file.filename,
        schema_id=schema_id,
        dataset_id=dataset_id,
    )

    # Build clients from app.state
    settings = get_settings()
    http_client = request.app.state.http_client
    validator_client = SchemaValidatorClient(http_client=http_client, base_url=settings.validator_url)
    registry_client = RegistryClient(http_client=http_client, base_url=settings.registry_url)

    # Launch async background task
    asyncio.create_task(
        process_csv_task(
            job_id=job.id,
            file_path=temp.name,
            schema_id=schema_id,
            dataset_id=dataset_id,
            session_factory=request.app.state.session_factory,
            validator_client=validator_client,
            registry_client=registry_client,
        )
    )

    return job


@jobs_router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    repo = JobRepository(db)
    # JobNotFound exception is handled by the registered exception handler
    job = await repo.get_job(job_id)
    return job