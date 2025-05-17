from pydantic import BaseModel


class JobCreate(BaseModel):
    job: str
