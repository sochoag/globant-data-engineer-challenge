from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException

import os

from ..database import get_db
from ..models import Department, Job, HiredEmployee
from .avro_utils import create_avro_backup, restore_table_from_avro, create_avro_full_backup, remove_file
from fastapi.responses import FileResponse

router = APIRouter(prefix="/avro")


@router.get("/backup/departments")
def backup_departments(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        filename = create_avro_backup(Department, db, "departments")

        background_tasks.add_task(remove_file, filename)

        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating backup: {str(e)}")


@router.get("/backup/jobs")
def backup_jobs(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        filename = create_avro_backup(Job, db, "jobs")

        background_tasks.add_task(remove_file, filename)

        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating backup: {str(e)}")


@router.get("/backup/employees")
def backup_employees(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    try:
        filename = create_avro_backup(HiredEmployee, db, "hired_employees")

        background_tasks.add_task(remove_file, filename)

        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type="application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating backup: {str(e)}")


@router.get("/backup/all")
def backup_all_tables(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    model_list = [Department, Job, HiredEmployee]

    filename = create_avro_full_backup(model_list, db)

    background_tasks.add_task(remove_file, filename)

    try:
        return FileResponse(
            path=filename,
            filename=os.path.basename(filename),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(filename)}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating backup: {str(e)}")


@router.post("/restore/departments")
def restore_departments(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return restore_table_from_avro(file, db, Department, "departments")


@router.post("/restore/jobs")
def restore_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return restore_table_from_avro(file, db, Job, "jobs")


@router.post("/restore/employees")
def restore_employees(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return restore_table_from_avro(file, db, HiredEmployee, "hired_employees")
