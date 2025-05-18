# Library imports
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local imports
from ..database import get_db
from .reports_utils import get_quarterly_hires, get_departments_above_average

# Router
router = APIRouter(prefix="/report")


@router.get("/quarterly_hires")
def backup_departments(db: Session = Depends(get_db)):
    data = get_quarterly_hires(db)
    return {
        "message": "Quarterly hires grouped by department and job",
        "data": data
    }


@router.get("/departments_above_average")
def backup_jobs(db: Session = Depends(get_db)):
    data = get_departments_above_average(db)
    return {
        "message": "Departments above average hired",
        "data": data
    }
