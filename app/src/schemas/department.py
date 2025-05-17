from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    department: str
