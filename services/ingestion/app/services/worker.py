import pandas as pd
import os
import json
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.repositories.job_repo import JobRepository
from app.clients.validator import SchemaValidatorClient, SchemaValidationError
from app.clients.registry_client import RegistryClient

logger = logging.getLogger(__name__)


async def process_csv_task(
    job_id: UUID,
    file_path: str,
    schema_id: UUID,
    dataset_id: UUID,
    session_factory: async_sessionmaker,
    validator_client: SchemaValidatorClient,
    registry_client: RegistryClient,
):
    """
    Async CSV processing worker.
    - Validates the first row against the schema via Validator service
    - Counts total rows
    - Registers a dataset version with Registry after success
    """
    async with session_factory() as session:
        repo = JobRepository(session)

        try:
            inferred_schema = None
            total_rows = 0
            file_size_bytes = os.path.getsize(file_path)

            await repo.update_job(job_id, status="in_progress")

            chunk_size = 10000

            for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunk_size)):
                if i == 0:
                    first_row = json.loads(chunk.iloc[0].to_json())
                    try:
                        await validator_client.validate_row(
                            schema_id=schema_id, payload=first_row
                        )
                    except SchemaValidationError as e:
                        await repo.update_job(
                            job_id, status="failed", error_message=str(e)
                        )
                        return

                    inferred_schema = chunk.dtypes.astype(str).to_dict()
                    await repo.update_job(
                        job_id,
                        status="in_progress",
                        inferred_schema=inferred_schema,
                    )

                total_rows += len(chunk)

            # Register version with Registry
            try:
                await registry_client.create_dataset_version(
                    dataset_id=str(dataset_id),
                    schema_snapshot=inferred_schema or {},
                    row_count=total_rows,
                    file_size_bytes=file_size_bytes,
                )
                await repo.update_job(
                    job_id,
                    status="completed",
                    row_count=total_rows,
                    dataset_id=dataset_id,
                )
            except Exception as e:
                logger.warning(f"Registry call failed for job {job_id}: {e}")
                await repo.update_job(
                    job_id,
                    status="completed_with_warnings",
                    row_count=total_rows,
                    error_message=f"CSV processed but Registry call failed: {e}",
                )

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            async with session_factory() as err_session:
                err_repo = JobRepository(err_session)
                await err_repo.update_job(
                    job_id, status="failed", error_message=str(e)
                )
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)