from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ingestion_job import IngestionJob
from app.exceptions import JobNotFound
import uuid
from typing import Optional


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(self, filename: str, schema_id: uuid.UUID, dataset_id: Optional[uuid.UUID] = None) -> IngestionJob:
        job = IngestionJob(
            filename=filename,
            schema_id=schema_id,
            dataset_id=dataset_id,
            status="pending"
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_job(self, job_id: uuid.UUID) -> IngestionJob:
        job = await self.session.get(IngestionJob, job_id)
        if not job:
            raise JobNotFound(job_id=str(job_id))
        return job

    async def update_job(
        self,
        job_id: uuid.UUID,
        status: str,
        row_count: Optional[int] = None,
        inferred_schema: Optional[dict] = None,
        error_message: Optional[str] = None,
        dataset_id: Optional[uuid.UUID] = None,
    ) -> IngestionJob:
        job = await self.session.get(IngestionJob, job_id)
        if not job:
            raise JobNotFound(job_id=str(job_id))

        job.status = status
        if row_count is not None:
            job.row_count = row_count
        if inferred_schema is not None:
            job.inferred_schema = inferred_schema
        if error_message is not None:
            job.error_message = error_message
        if dataset_id is not None:
            job.dataset_id = dataset_id

        await self.session.commit()
        await self.session.refresh(job)
        return job
