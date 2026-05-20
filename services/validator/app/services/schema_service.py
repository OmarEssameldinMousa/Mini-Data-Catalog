from app.repositories.schema_repo import SchemaRepository
from app.schemas.field import FieldDefinition
import uuid
from app.models.schema import Schema
from app.models.schema_version import SchemaVersion
from app.models.validation_result import ValidationResult


class SchemaService:
    def __init__(self, repo: SchemaRepository):
        self.repo = repo

    async def create_new_schema(
            self, name: str, 
            description: str, 
            owner: str, 
            initial_fields: list[FieldDefinition]
        ) -> Schema:
        new_schema = await self.repo.create_schema(
            name=name,
            description=description,
            owner=owner
        )
        
        initial_fields_dicts = [f.model_dump() for f in initial_fields]

        first_schema_version = await self.repo.create_version(
            new_schema.id,
            field_definitions=initial_fields_dicts, 
            version_number='v1', 
            is_breaking=False,
            changelog="first version"
        )

        return new_schema
    

    async def compare_versions(self,old_fields: list[FieldDefinition], new_fields: list[FieldDefinition])-> dict:
        """
        The diff engine.
        Return a dict with three keys: 'added', 'removed', 'changed'.
        """
        old_fields_map = {f.name: f for f in old_fields}
        new_fields_map = {f.name: f for f in new_fields}

        added = []
        removed = []
        changed = []

        for field_name, field in new_fields_map.items():
            
            if field_name not in old_fields_map:
                added.append(field)
                continue

            
            old_field = old_fields_map[field_name]

            if field != old_field:
                changed.append(
                    {
                        "old": old_field,
                        "new": field
                    }
                )
        for field_name, field in old_fields_map.items():
            if field_name not in new_fields_map:
                removed.append(field)
        
        return {"added": added, "removed": removed, "changed":changed}
        
    async def add_schema_version(self, schema_id: uuid.UUID, new_fields: list[FieldDefinition], new_version_number: str) -> SchemaVersion:
        
        schema = await self.repo.get_schema_by_id(schema_id=schema_id)
        
        if not schema:
            raise ValueError("Schema not found")
        
        # get the current active version 
        current_version = await self.repo.get_current_active_schema_version(schema_id=schema_id)

        current_version_fields = [FieldDefinition.model_validate(f) for f in current_version.field_definitions]
        # compare the new fields with the current version fields
        diff_result = await self.compare_versions(current_version_fields, new_fields)

        # determine if the new version is breaking or not
        is_breaking = len(diff_result["removed"]) > 0 or len(diff_result["changed"]) > 0

        await self.repo.update_schema_version_status(version_id=current_version.id, is_current=False) 

        changelog = f"Version {new_version_number} created with {len(diff_result['added'])} added fields, {len(diff_result['removed'])} removed fields, and {len(diff_result['changed'])} changed fields."
        
        # create the new schema version
        
        field_definitions_dicts = [f.model_dump() for f in new_fields]

        new_version = await self.repo.create_version(
            schema_id=schema_id,
            field_definitions=field_definitions_dicts,
            version_number=new_version_number,
            is_breaking=is_breaking,
            changelog=changelog if is_breaking else "Non-breaking changes",
            is_current=True
        )

        return new_version
    
    async def save_validation_result(self, schema_version_id: uuid.UUID, is_valid: bool, error_report: dict, payload_hash: str) -> ValidationResult:
        return await self.repo.save_validation_result(
            schema_version_id=schema_version_id,
            is_valid=is_valid,
            error_report=error_report,
            payload_hash=payload_hash
        )
    
    async def get_schema_with_version(self, schema_id: uuid.UUID, version_number: str)-> SchemaVersion:
        schema = None
        if version_number == "active":
            schema = await self.repo.get_current_active_schema_version(schema_id=schema_id)
        else:
            schema = await self.repo.get_schema_with_version(schema_id=schema_id, version_number=version_number)
        return schema
    
    async def get_schema_version_stats(self, schema_version_id: uuid.UUID) -> dict:
        stats = await self.repo.get_version_stats(schema_version_id=schema_version_id)    
        total = stats["total_runs"]
        success = stats["successful_runs"]

        stats["pass_rate"] = success / total if total > 0 else 0
        return stats