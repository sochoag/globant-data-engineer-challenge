from fastapi import HTTPException
from datetime import datetime

MAX_RECORDS_PER_REQUEST = 1000


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
