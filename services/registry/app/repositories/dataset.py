# services/registry/app/repositories/dataset.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from typing import Optional, List

from app.models.dataset import Dataset
from app.models.tag import Tag
from app.models.db_enums.enums import DataFormatEnum, StatusEnum
from app.schemas.dataset import DatasetRead, DatasetCreate, DatasetUpdate
from app.models.dataset_version import DatasetVersion
from app.schemas.version import DataSetVersionCreate, DataSetVersionRead

class DatasetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, dataset_id: str) -> Dataset | None:
        stmt = (
            select(Dataset)
            .options(selectinload(Dataset.tags),
                     selectinload(Dataset.versions)
                     )
            .where(Dataset.id == dataset_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, dataset_in: DatasetCreate) -> Dataset:
        dataset_data = dataset_in.model_dump(exclude={"tags", "versions"})
        db_dataset =  Dataset(**dataset_data)

        tag_names = dataset_in.tags or [] # tag names
        result = await self.session.execute(select(Tag).where(Tag.name.in_(tag_names)))
        db_tags = result.scalars().all() 
        db_tags_map = {tag.name: tag for tag in db_tags}
        
        existing_tags = [db_tags_map[tag_name] for tag_name in tag_names if tag_name in db_tags_map]
        not_existing_tags = [tag_name for tag_name in tag_names if tag_name not in db_tags_map]

        db_dataset.tags.extend(existing_tags)
        
        if not_existing_tags:
            not_existing = []  

            for tag in not_existing_tags:
                new_tag = Tag(name=tag)
                self.session.add(new_tag)
                not_existing.append(new_tag)

            db_dataset.tags.extend(not_existing)

        # Creat the first version - must be provided in the requet body
        version_data = dataset_in.versions[0] 

        version_data_dict = version_data.model_dump()
        new_version = DatasetVersion(**version_data_dict)
        db_dataset.versions.append(new_version)

        self.session.add(db_dataset)
        await self.session.commit()
        await self.session.refresh(db_dataset)
        return db_dataset 
    
    async def get_all(
            self, 
            limit: int, 
            offset: int,
            owner: Optional[str] = None,
            data_format: Optional[DataFormatEnum] = None
    ) -> tuple[list[Dataset], int]:
        
        query = select(Dataset).options(selectinload(Dataset.tags),selectinload(Dataset.versions))

        if owner:
            query = query.where(Dataset.owner == owner)
        
        if data_format:
            query = query.where(Dataset.data_format == data_format)

        query = query.offset(offset).limit(limit)

        datasets = await self.session.execute(query)
        datasets = datasets.scalars().all()
        
        count_query = select(func.count()).select_from(Dataset)
        if owner:
            count_query = count_query.where(Dataset.owner == owner)
        if data_format:
            count_query = count_query.where(Dataset.data_format == data_format)
            
        total_count = await self.session.execute(count_query)
        total_count = total_count.scalar()

        return list(datasets), total_count


    async def update(self, dataset_id: str, dataset_in: DatasetUpdate) -> Dataset | None:
        dataset = await self.get_by_id(dataset_id)

        if not dataset:
            return None
        
        update_data = dataset_in.model_dump(exclude_unset=True, exclude={"tags"})
        
        for field, value in update_data.items():
            setattr(dataset, field, value)
        
        if dataset_in.tags is not None:
            new_tag_names = set(dataset_in.tags)
            current_tag_names = set(tag.name for tag in dataset.tags)

            tags_to_add = new_tag_names - current_tag_names
            tags_to_remove = current_tag_names - new_tag_names

            if tags_to_add:
                result = await self.session.execute(select(Tag).where(Tag.name.in_(tags_to_add)))
                db_tags_to_add = result.scalars().all()
                db_tags_map = {tag.name: tag for tag in db_tags_to_add}

                for tag_name in tags_to_add:
                    if tag_name in db_tags_map:
                        dataset.tags.append(db_tags_map[tag_name])
                    else:
                        new_tag = Tag(name=tag_name)
                        self.session.add(new_tag)
                        dataset.tags.append(new_tag)

            if tags_to_remove:
                dataset.tags = [tag for tag in dataset.tags if tag.name not in tags_to_remove]

        await self.session.commit()
        await self.session.refresh(dataset)
        
        return dataset
    

    async def soft_delete(self, dataset_id: str) -> Dataset | None:

        dataset = await self.get_by_id(dataset_id)
        
        if not dataset:
            return False
        
        dataset.status = StatusEnum.DEPRECATED

        await self.session.commit()
        await self.session.refresh(dataset)
        return True

    async def permanent_delete(self, dataset_id: str) -> bool:
        dataset = await self.get_by_id(dataset_id)
        
        if not dataset:
            return False
        
        await self.session.delete(dataset)
        await self.session.commit()
        return True

    async def get_versions(self, dataset_id: str, limit: int, offset: int) -> tuple[List[DatasetVersion], int]:
        query = select(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id).offset(offset).limit(limit)
        result = await self.session.execute(query)
        versions = result.scalars().all()
        
        count_query = select(func.count()).select_from(DatasetVersion).where(DatasetVersion.dataset_id == dataset_id)
        total_count = await self.session.execute(count_query)
        total_count = total_count.scalar()
        
        return list(versions), total_count
    
        

    async def create_version(self, dataset_id: str, version_data: DataSetVersionCreate) -> DatasetVersion:
        version_data_dict = version_data.model_dump()
        new_version = DatasetVersion(**version_data_dict)
        new_version.dataset_id = dataset_id

        self.session.add(new_version)
        await self.session.commit()
        await self.session.refresh(new_version)
        
        return new_version

    async def get_version_by_id(self, dataset_id: str, version_id: str) -> DatasetVersion | None:
        query = select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.id == version_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_version(self, dataset_id: str, version_id: str, version_data: DataSetVersionCreate) -> DatasetVersion | None:
        version = await self.get_version_by_id(dataset_id, version_id)
        
        if not version:
            return None
        
        update_data = version_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(version, field, value)

        await self.session.commit()
        await self.session.refresh(version)
        
        return version

    async def delete_version(self, dataset_id: str, version_id: str) -> bool:
        version = await self.get_version_by_id(dataset_id, version_id)
        
        if not version:
            return False
        
        await self.session.delete(version)
        await self.session.commit()
        return True
