from pydantic import BaseModel
from datetime import datetime


class HiredEmployeeCreate(BaseModel):
    name: str
    datetime: datetime
    department_id: int
    job_id: int
