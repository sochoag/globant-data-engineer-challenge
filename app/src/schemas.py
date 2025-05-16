from pydantic import BaseModel, field_validator
from typing import List, Union
from datetime import datetime


class DepartmentCreate(BaseModel):
    department: str


class JobCreate(BaseModel):
    job: str


class HiredEmployeeCreate(BaseModel):
    name: str
    datetime: datetime
    department_id: int
    job_id: int


PostRequest = Union[dict, List[dict]]
