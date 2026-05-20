from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func , case
from sqlalchemy.orm import selectinload
from app.models.schema import Schema
from app.models.schema_version import SchemaVersion
import uuid

from app.models.validation_result import ValidationResult 

class SchemaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_schema(self, name: str, description: str, owner: str ) -> Schema:
        
        new_schema = Schema(
            name=name,
            description=description,
            owner=owner
        )

        self.session.add(new_schema)
        await self.session.flush()
        return new_schema
    
    async def get_schema_by_id(self, schema_id: uuid.UUID) -> Schema | None:
        query = select(Schema).options(selectinload(Schema.versions)).where(Schema.id == schema_id)

        result = await self.session.execute(query) 

        schema = result.scalar_one_or_none()

        return schema
    
    async def create_version(self, 
                       schema_id: uuid.UUID, 
                       field_definitions: list[dict], 
                       version_number:str, 
                       is_breaking: bool,
                       changelog: str,
                       is_current: bool = True
        ) -> SchemaVersion:
        new_version = SchemaVersion(
            schema_id=schema_id,
            field_definitions=field_definitions,
            version_number=version_number,
            is_breaking=is_breaking,
            changelog=changelog,
            is_current=is_current
        )

        self.session.add(new_version)
        await self.session.flush()

        return new_version
    
    async def get_current_active_schema_version(self, schema_id: uuid.UUID) -> SchemaVersion | None:
        query = (
            select(SchemaVersion)
            .options(selectinload(SchemaVersion.validationresult))
            .where(
                SchemaVersion.schema_id == schema_id,
                SchemaVersion.is_current.is_(True)
            )
        )
        result = await self.session.execute(query)

        return result.scalar_one_or_none()
    
    async def update_schema_version_status(self, version_id: uuid.UUID, is_current: bool):
        version = await self.session.get(SchemaVersion, version_id)
        if version:
            version.is_current = is_current
            await self.session.flush()
        
    async def save_validation_result(self, schema_version_id: uuid.UUID, is_valid: bool, error_report: dict, payload_hash: str) -> ValidationResult:
        new_result = ValidationResult(
            schema_version_id=schema_version_id,
            is_valid=is_valid,
            error_report=error_report,
            payload_hash=payload_hash
        )

        self.session.add(new_result)
        await self.session.flush()

        return new_result

    async def get_version_stats(self, schema_version_id: uuid.UUID) -> dict:
        stmt = select(
            func.count(ValidationResult.id).label("total_runs"),
            func.sum(case((ValidationResult.is_valid == True, 1), else_=0)).label("successful_runs")
        ).where(ValidationResult.schema_version_id == schema_version_id)

        result = await self.session.execute(stmt)
        row = result.one()
        return {"total_runs": row.total_runs, "successful_runs": row.successful_runs}
            

    async def get_schema_with_version(self, schema_id: uuid.UUID, version_number: str) -> SchemaVersion | None:
        
        stmt = select(SchemaVersion).where(
            SchemaVersion.schema_id ==  schema_id, 
            SchemaVersion.version_number == version_number
        ).order_by(SchemaVersion.created_at.desc())

        result = await self.session.execute(stmt)
        schema_version = result.scalars().first()

        return schema_version