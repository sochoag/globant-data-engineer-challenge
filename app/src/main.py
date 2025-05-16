from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .models import Department
from .database import SessionLocal
from .schemas import *

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "message": error["msg"]
        } for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation failed",
            "errors": errors
        }
    )


@app.post("/departments/")
def create_departments(request: DepartmentRequest, db: Session = Depends(get_db)):
    if isinstance(request, DepartmentCreate):
        department_list = [request]
    elif isinstance(request, list):
        department_list = request
    else:
        return {"message": "Invalid request", "error": "Request must be a Department or a list of Departments"}

    success_registers = []
    errors = []

    for dept in department_list:
        try:
            db_dept = Department(department=dept.department)
            db.add(db_dept)
            db.flush()
            success_registers.append(dept)
        except Exception as e:
            errors.append({"department": dept.department, "error": str(e)})
            db.rollback()
    db.commit()

    return {
        "message": f"{len(success_registers)} department(s) created successfully",
        "failed": errors if errors else None
    }
