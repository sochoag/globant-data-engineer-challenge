from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas import PostRequest
from ..database import get_db
from ..models import Department, Job, HiredEmployee
from .api_utils import *

router = APIRouter()

error_log_file = "./.data/api_errors.txt"


@router.post("/departments/")
def create_departments(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        department_list = [request]
    elif isinstance(request, list):
        department_list = request
    else:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                "Invalid request: Request must be a register or a list of registers\n")
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(department_list)

    success_registers, errors = batch_create(
        db, Department, department_list)

    if errors:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"{len(errors)} department(s) failed to create\n")
    return {
        "message": f"{len(success_registers)} department(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }


@router.post("/jobs/")
def create_jobs(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        job_list = [request]
    elif isinstance(request, list):
        job_list = request
    else:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                "Invalid request: Request must be a register or a list of registers\n")
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(job_list)

    success_registers, errors = batch_create(
        db, Job, job_list)

    if errors:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"{len(errors)} job(s) failed to create\n")

    return {
        "message": f"{len(success_registers)} job(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }


@router.post("/employees/")
def create_employees(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        employee_list = [request]
    elif isinstance(request, list):
        employee_list = request
    else:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                "Invalid request: Request must be a register or a list of registers\n")
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(employee_list)

    success_registers, errors = batch_create(
        db, HiredEmployee, employee_list)

    if errors:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"{len(errors)} employee(s) failed to create\n")

    return {
        "message": f"{len(success_registers)} employee(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }
