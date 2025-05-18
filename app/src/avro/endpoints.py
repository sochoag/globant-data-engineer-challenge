# Library imports
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

# Local imports
from ..database import get_db
from ..models import Department, Job, HiredEmployee
from .avro_utils import create_avro_backup, restore_table_from_avro, create_avro_full_backup, remove_file

# Router
router = APIRouter(prefix="/avro")


@router.get("/backup/departments")
def backup_departments(db: Session = Depends(get_db), background_tasks: BackgroundTasks = None):
    """
    Backup the departments table.

    Parameters:
    - db (Session): The SQLAlchemy session to the database.
    - background_tasks (BackgroundTasks): Background tasks.

    Returns:
    - FileResponse: The response containing the backup file.
    """
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
    """
    Backup the jobs table.

    Parameters:
    - db (Session): The SQLAlchemy session to the database.
    - background_tasks (BackgroundTasks): Background tasks.

    Returns:
    - FileResponse: The response containing the backup file.
    """
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
    """
    Backup the employees table.

    Parameters:
    - db (Session): The SQLAlchemy session to the database.
    - background_tasks (BackgroundTasks): Background tasks.

    Returns:
    - FileResponse: The response containing the backup file.
    """
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
    """
    Backup of all tables in the database.

    Parameters:
    - db (Session): The SQLAlchemy session to the database.
    - background_tasks (BackgroundTasks): Background tasks.

    Returns:
    - FileResponse: The response containing the backup file.
    """
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
    """
    Restore the departments table.

    Parameters:
    - file (UploadFile): The file to be restored.
    - db (Session): The SQLAlchemy session to the database.

    Returns:
    - dict: A dictionary containing the message and success/failed records.
    """
    return restore_table_from_avro(file, db, Department, "departments")


@router.post("/restore/jobs")
def restore_jobs(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Restore the jobs table.

    Parameters:
    - file (UploadFile): The file to be restored.
    - db (Session): The SQLAlchemy session to the database.

    Returns:
    - dict: A dictionary containing the message and success/failed records.
    """
    return restore_table_from_avro(file, db, Job, "jobs")


@router.post("/restore/employees")
def restore_employees(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Restore the employees table.

    Parameters:
    - file (UploadFile): The file to be restored.
    - db (Session): The SQLAlchemy session to the database.

    Returns:
    - dict: A dictionary containing the message and success/failed records.
    """
    return restore_table_from_avro(file, db, HiredEmployee, "hired_employees")
