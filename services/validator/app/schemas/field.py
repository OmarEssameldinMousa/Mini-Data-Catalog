from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Any
import re


class FieldConstraints(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    enum_values: Optional[List[Any]] = None

    @model_validator(mode="after")
    def check_min_max_logic(self) -> "FieldConstraints":
        if self.min_length is not None and self.max_length is not None:
            if self.min_length > self.max_length:
                raise ValueError("min_length can't be greater than max_length")

        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("min_value can't be greater than max_value")

        if self.enum_values is not None:
            if len(self.enum_values) == 0:
                raise ValueError("can't provide empty enum_values")

        if self.pattern is not None:
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")

        return self


class FieldDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    nullable: bool = False
    constraints: Optional[FieldConstraints] = None

    @field_validator("name")
    @classmethod
    def validate_name_snake_case(cls, v: str) -> str:
        if not v:
            raise ValueError("name cannot be empty")

        if v[0].isnumeric():
            raise ValueError("name can't start with numbers")

        if re.fullmatch(r"[a-z]+(_[a-z0-9]+)*$", v) is None:
            raise ValueError("name must be snake case pattern")

        return v

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: str) -> str:
        v = v.lower()

        type_map = {
            "int": "integer",
            "str": "string",
            "bool": "boolean",
        }

        v = type_map.get(v, v)

        allowed = {"integer", "string", "float", "boolean", "array", "object"}
        if v not in allowed:
            raise ValueError(f"Type '{v}' is invalid. Allowed types: {allowed}")

        return v

    @model_validator(mode="after")
    def validate_constraints_against_type(self) -> "FieldDefinition":
        if self.constraints is None:
            return self

        if self.type in ("integer", "float"):
            if (
                self.constraints.min_length is not None
                or self.constraints.max_length is not None
                or self.constraints.pattern is not None
            ):
                raise ValueError(
                    "type integer or float can't have min_length, max_length, or pattern constraints"
                )

        elif self.type == "string":
            if (
                self.constraints.min_value is not None
                or self.constraints.max_value is not None
            ):
                raise ValueError(
                    "type string can't have min_value, max_value constraints"
                )

        return self