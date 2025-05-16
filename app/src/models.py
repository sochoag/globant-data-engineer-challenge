from sqlalchemy import Column, Integer, String
from .database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String, nullable=False)
