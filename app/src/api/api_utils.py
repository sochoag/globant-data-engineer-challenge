# Library imports
from fastapi import HTTPException
from datetime import datetime

# Constants
MAX_RECORDS_PER_REQUEST = 1000
error_log_file = "./.data/api_errors.txt"

# Function for validating record limit


def validate_record_limit(data):
    """
    Validate the record limit.

    Args:
        data: The data to be validated.

    Raises:
        HTTPException: If the record limit is exceeded.
    """
    if len(data) > MAX_RECORDS_PER_REQUEST:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"You can only send {MAX_RECORDS_PER_REQUEST} records at a time\n")
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"You can only send {MAX_RECORDS_PER_REQUEST} records at a time",
                "total_records": len(data)
            }
        )

# Function for batch creating records


def batch_create(db, model_class, model_list):
    """
    Batch create records.

    Args:
        db: The database connection.
        model_class: The model class.
        model_list: The list of model instances.

    Returns:
        list: A list of successfully inserted records.
        list: A list of failed records.
    """
    successfully_inserted = []
    failed_records = []

    for item in model_list:
        try:
            # Extract values based on data type
            raw_data = item

            # Filter fields that don't exist in the model
            model_columns = model_class.__table__.columns.keys()
            filtered_data = {
                key: value for key, value in raw_data.items() if key in model_columns
            }

            # Automatic type and field validation
            missing_fields = []
            type_errors = []

            for col_name, column in model_class.__table__.columns.items():
                if col_name not in filtered_data:
                    if not column.nullable and col_name != "id":
                        missing_fields.append(col_name)
                    continue

                value = filtered_data[col_name]
                expected_type = column.type.python_type

                # Try to validate type
                if not isinstance(value, expected_type):
                    try:
                        # Try to convert to basic type if possible
                        if expected_type == int and isinstance(value, str) and value.isdigit():
                            filtered_data[col_name] = int(value)
                        elif expected_type == float and isinstance(value, (int, str)) and str(value).replace('.', '', 1).isdigit():
                            filtered_data[col_name] = float(value)
                        elif expected_type == datetime:
                            filtered_data[col_name] = datetime.strptime(
                                value, "%Y-%m-%d %H:%M:%S")
                        else:
                            with open(error_log_file, "a") as error_log:
                                error_log.write(
                                    f"Value '{value}' is not of type {expected_type.__name__}\n")
                            raise TypeError(
                                f"Value '{value}' is not of type {expected_type.__name__}")
                    except Exception as te:
                        type_errors.append(f"{col_name}: {te}")

            if missing_fields:
                # Insert missing fields at the beginning of the list
                type_errors.insert(
                    0, f"Missing required fields: {', '.join(missing_fields)}")

            if type_errors:
                # Raise a ValueError with the joined type errors
                raise ValueError("; ".join(type_errors))

            # Create an instance of the model and save it
            db_item = model_class(**filtered_data)
            db.add(db_item)
            db.flush()
            db.commit()
            successfully_inserted.append(raw_data)

        except Exception as e:
            # Add the record and error to the failed records list
            failed_records.append({
                "record": raw_data,
                "error": str(e)
            })
            db.rollback()
            db.expire_all()

        if failed_records:
            with open(error_log_file, "a") as error_log:
                error_log.write(
                    f"Failed to create {len(failed_records)} records in {model_class.__tablename__}\nFailed records:\n{failed_records}\n")

    return successfully_inserted, failed_records
