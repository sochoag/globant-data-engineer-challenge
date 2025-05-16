from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from sqlalchemy import orm
from typing import List, Union

# Local imports
from .models import Department, Job, HiredEmployee
from .database import SessionLocal
from .schemas import *

app = FastAPI()

# Global configs
MAX_RECORDS_PER_REQUEST = 1000

# Create the database connection


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
            "field": ".".join(map(str, error["loc"])),
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


def validate_record_limit(data):
    if len(data) > MAX_RECORDS_PER_REQUEST:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"You can only send {MAX_RECORDS_PER_REQUEST} records at a time",
                "total_records": len(data)
            }
        )


def batch_create(db, model_class, model_list):
    successfully_inserted = []
    failed_records = []

    for item in model_list:
        try:
            # Extraer valores según tipo de dato

            raw_data = item

            # Filtrar campos que no existen en el modelo
            model_columns = model_class.__table__.columns.keys()
            filtered_data = {
                key: value for key, value in raw_data.items() if key in model_columns
            }

            # Validación automática de tipos y campos obligatorios
            missing_fields = []
            type_errors = []

            for col_name, column in model_class.__table__.columns.items():
                if col_name not in filtered_data:
                    if not column.nullable and col_name != "id":
                        missing_fields.append(col_name)
                    continue

                value = filtered_data[col_name]
                expected_type = column.type.python_type

                # Intentar validar tipo

                if not isinstance(value, expected_type):
                    try:
                        # Intentar conversión básica si es posible
                        if expected_type == int and isinstance(value, str) and value.isdigit():
                            filtered_data[col_name] = int(value)
                        elif expected_type == str and isinstance(value, (int, float)):
                            filtered_data[col_name] = str(value)
                        elif expected_type == float and isinstance(value, (int, str)) and str(value).replace('.', '', 1).isdigit():
                            filtered_data[col_name] = float(value)
                        elif expected_type == datetime:
                            filtered_data[col_name] = datetime.strptime(
                                value, "%Y-%m-%d %H:%M:%S")
                        else:
                            raise TypeError(
                                f"Value '{value}' is not of type {expected_type.__name__}")
                    except Exception as te:
                        type_errors.append(f"{col_name}: {te}")

            if missing_fields:
                type_errors.insert(
                    0, f"Missing required fields: {', '.join(missing_fields)}")

            if type_errors:
                raise ValueError("; ".join(type_errors))

            # Crear instancia del modelo y guardar
            db_item = model_class(**filtered_data)
            db.add(db_item)
            db.flush()
            db.commit()
            successfully_inserted.append(raw_data)

        except Exception as e:
            failed_records.append({
                "record": raw_data,
                "error": str(e)
            })
            db.rollback()
            db.expire_all()

    return successfully_inserted, failed_records


@app.post("/departments/")
def create_departments(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        department_list = [request]
    elif isinstance(request, list):
        department_list = request
    else:
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(department_list)

    success_registers, errors = batch_create(
        db, Department, department_list)

    return {
        "message": f"{len(success_registers)} department(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }


@app.post("/jobs/")
def create_jobs(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        job_list = [request]
    elif isinstance(request, list):
        job_list = request
    else:
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(job_list)

    success_registers, errors = batch_create(
        db, Job, job_list)

    return {
        "message": f"{len(success_registers)} job(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }


@app.post("/employees/")
def create_employees(request: PostRequest, db: Session = Depends(get_db)):
    if isinstance(request, dict):
        employee_list = [request]
    elif isinstance(request, list):
        employee_list = request
    else:
        return {"message": "Invalid request", "error": "Request must be a register or a list of registers"}

    validate_record_limit(employee_list)

    success_registers, errors = batch_create(
        db, HiredEmployee, employee_list)

    return {
        "message": f"{len(success_registers)} employee(s) created successfully",
        "success": success_registers,
        "failed": errors if errors else None
    }
