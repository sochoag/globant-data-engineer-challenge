from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Create the tables
# Define the Department model
class Department(Base):
  __tablename__ = 'departments'

  id = Column(Integer, primary_key=True)
  department = Column(String(100), nullable=False)

  employees = relationship('HiredEmployee', back_populates='department')

# Define the Job model
class Job(Base):
  __tablename__ = 'jobs'

  id = Column(Integer, primary_key=True)
  job = Column(String(100), nullable=False)

  employees = relationship('HiredEmployee', back_populates='job')

# Define the HiredEmployee model
class HiredEmployee(Base):
  __tablename__ = 'hired_employees'

  id = Column(Integer, primary_key=True)
  name = Column(String(100), nullable=False)
  datetime = Column(DateTime, nullable=False)
  department_id = Column(Integer, ForeignKey('departments.id'), nullable=False)
  job_id = Column(Integer, ForeignKey('jobs.id'), nullable=False)

  department = relationship('Department', back_populates='employees')
  job = relationship('Job', back_populates='employees')