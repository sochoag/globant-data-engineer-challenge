from pydantic import BaseModel, field_validator
from typing import List, Union


class DepartmentCreate(BaseModel):
    department: str

    @field_validator("department")
    def string_validation(cls, v):
        if not isinstance(v, str):
            raise ValueError("department must be a string")
        return v.strip()


DepartmentRequest = Union[DepartmentCreate, List[DepartmentCreate]]
