# app/services/dataset.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple
from app.repositories.dataset import DatasetRepository
from app.exceptions import DatasetNotFound, VersionNotFound
from app.schemas.dataset import DatasetCreate, DatasetUpdate
from app.schemas.version import DataSetVersionCreate
from app.models.db_enums.enums import DataFormatEnum
# services/registry/app/services/dataset.py
class DatasetService:
    """
    Business logic layer. Raises domain exceptions, never HTTPException.
    Decides what to do with None returns from the repository.
    """

    def __init__(self, session: AsyncSession):
        self.repo = DatasetRepository(session)

    async def get_dataset(self, dataset_id: str):
        """
        Calls repo.get_by_id — if None, raises DatasetNotFound.
        This is the layer that makes the 'not found' decision.
        """
        dataset = await self.repo.get_by_id(dataset_id)
        if not dataset:
            raise DatasetNotFound(dataset_id=dataset_id)
        return dataset

    async def create_dataset(self, dataset_in: DatasetCreate):
        return await self.repo.create(dataset_in)

    async def get_datasets(self, limit: int = 10, offset: int = 0, owner: Optional[str] = None, data_format: Optional[DataFormatEnum] = None):
        return await self.repo.get_all(limit=limit, offset=offset, owner=owner, data_format=data_format)

    async def update_dataset(self, dataset_id: str, dataset_in: DatasetUpdate):
        dataset = await self.repo.update(dataset_id, dataset_in)
        if not dataset:
            raise DatasetNotFound(dataset_id=dataset_id)
        return dataset

    async def soft_delete_dataset(self, dataset_id: str):
        success = await self.repo.soft_delete(dataset_id)
        if not success:
            raise DatasetNotFound(dataset_id=dataset_id)
        return True

    async def permanent_delete_dataset(self, dataset_id: str):
        success = await self.repo.permanent_delete(dataset_id)
        if not success:
            raise DatasetNotFound(dataset_id=dataset_id)
        return True

    async def get_dataset_versions(self, dataset_id: str, limit: int = 10, offset: int = 0):
        await self.get_dataset(dataset_id)
        datasets, total = await self.repo.get_versions(dataset_id, limit, offset)
        return datasets, total

    async def create_dataset_version(self, dataset_id: str, version_data: DataSetVersionCreate, validator_client: 'ValidatorClient' = None):
        from sqlalchemy.exc import IntegrityError
        
        if version_data.validator_schema_id and validator_client:
            await validator_client.validate(
                schema_id=version_data.validator_schema_id,
                payload=version_data.schema_snapshot
            )

        try:
            return await self.repo.create_version(dataset_id, version_data)
        except IntegrityError:
            # If dataset_id fk constraint fails
            raise DatasetNotFound(dataset_id=dataset_id)

    async def get_dataset_version(self, dataset_id: str, version_id: str):
        version = await self.repo.get_version_by_id(dataset_id, version_id)
        if not version:
            raise VersionNotFound(version_id=version_id)
        return version

    async def update_dataset_version(self, dataset_id: str, version_id: str, version_data: DataSetVersionCreate):
        version = await self.repo.update_version(dataset_id, version_id, version_data)
        if not version:
            raise VersionNotFound(version_id=version_id)
        return version

    async def delete_dataset_version(self, dataset_id: str, version_id: str):
        success = await self.repo.delete_version(dataset_id, version_id)
        if not success:
            raise VersionNotFound(version_id=version_id)
        return True