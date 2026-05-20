with open('services/validator/app/routers/validation.py', 'r') as f:
    content = f.read()

content = content.replace("def validate_payload(", "async def validate_payload(")
content = content.replace("current_active_version = repo.get_current_active_schema_version(schema_id)", "current_active_version = await repo.get_current_active_schema_version(schema_id)")
content = content.replace("result = engine.validate(payload)", "result = await engine.validate(payload)")
content = content.replace("validation_result = repo.save_validation_result(", "validation_result = await repo.save_validation_result(")

with open('services/validator/app/routers/validation.py', 'w') as f:
    f.write(content)
