from typing import Optional, Any, List, Dict
from app.schemas.field import FieldDefinition
from app.schemas.validation import ValidationReport, FieldError
from app.models.db_enums.enums import ErrorCodesEnum

import re
# errors "FIELD_MISSING", "TYPE_MISMATCH", "CONSTRAINT_VIOLATION"
class ValidationEngine:
    def __init__(self, fields: List[FieldDefinition], strict_mode: bool = False):
        """
        strict_mode: If True, any fileds in the payload not defined in the schema will cause a FIELD_UNKNOWN error
        """
        self.fields = {f.name: f for f in fields}
        self.strict_mode = strict_mode

    def validate(self, payload: Dict[str, Any]) -> ValidationReport:
        errors: List[FieldError] = []

        # check for unknown fields
        # 1️⃣ Check for unknown fields
        if self.strict_mode:
            for field in payload:
                if field not in self.fields:
                    errors.append(
                        FieldError(
                            field=field,
                            code=ErrorCodesEnum.FIELD_UNKNOWN.value,
                            message=f"{field} field is not defined in the schema.",
                            received=payload[field],
                            expected="defined field"
                        )
                    )
        
        # Iterate through expected schema fields and validate
        for field_name, field_def in self.fields.items():
            # Check for missing fields
            if field_name not in payload:
                if not field_def.nullable:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.FIELD_MISSING.value,
                            message=f"{field_name} is missing.",
                            received=None,
                            expected=field_def.type
                        )
                    )
                continue  
            
            value = payload[field_name]
            
            # nullability check
            if value is None:
                if not field_def.nullable:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.NULL_VIOLATION.value,
                            message=f"{field_name} is not nullable",
                            received=value,
                            expected=field_def.type
                        )
                    )
                continue

            # Type check
            if self._check_type_mismatch(value, field_def.type):
                errors.append(
                    FieldError(
                        field=field_name,
                        code=ErrorCodesEnum.TYPE_MISMATCH.value,
                        message=f"Expected type '{field_def.type}' but got '{type(value).__name__}'",
                        received=value,
                        expected=field_def.type
                    )
                )
                continue

            c = field_def.constraints
            if not c:
                continue
        
            # Enum constraint
            if c.enum_values and value not in c.enum_values:
                errors.append(
                    FieldError(
                        field=field_name,
                        code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                        message=f"{field_name} must be one of {c.enum_values}",
                        received=value,
                        expected=c.enum_values
                    )
                )


            # Numeric constraints
            if field_def.type in ("integer", "float"):

                if c.min_value is not None and value < c.min_value:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                            message=f"{field_name} must be >= {c.min_value}",
                            received=value,
                            expected=f">= {c.min_value}"
                        )
                    )

                if c.max_value is not None and value > c.max_value:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                            message=f"{field_name} must be <= {c.max_value}",
                            received=value,
                            expected=f"<= {c.max_value}"
                        )
                    )

            # String constraints
            if field_def.type == "string":

                if c.min_length is not None and len(value) < c.min_length:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                            message=f"{field_name} length must be >= {c.min_length}",
                            received=value,
                            expected=f"length >= {c.min_length}"
                        )
                    )

                if c.max_length is not None and len(value) > c.max_length:
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                            message=f"{field_name} length must be <= {c.max_length}",
                            received=value,
                            expected=f"length <= {c.max_length}"
                        )
                    )

                if c.pattern and not re.match(c.pattern, value):
                    errors.append(
                        FieldError(
                            field=field_name,
                            code=ErrorCodesEnum.CONSTRAINT_VIOLATION.value,
                            message=f"{field_name} does not match required pattern",
                            received=value,
                            expected=c.pattern
                        )
                    )

        # Final validation report
        is_valid = len(errors) == 0
        return ValidationReport(valid=is_valid, errors=errors)

    def _check_type_mismatch(self, v: Any, field_type: str) -> bool:
        
        type_map = {
            "integer": int,
            "string": str,
            "boolean" : bool,
            "float": float,
            "object": dict,
            "array": list
        }   
        expected_type = type_map.get(field_type)
        if expected_type is None:
            return True
        return type(v) is not expected_type