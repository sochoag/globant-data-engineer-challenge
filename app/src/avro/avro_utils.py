import os
import fastavro
from datetime import datetime
from fastapi import HTTPException
from zipfile import ZipFile
from tempfile import TemporaryDirectory
from sqlalchemy import text

error_log_file = "./.data/avro_errors.txt"

backup_folder = TemporaryDirectory(dir=".", prefix="backup")
BACKUP_DIR = backup_folder.name


def create_avro_backup(model, db, table_name, backup_dir=BACKUP_DIR):
    # Obtain all records from the database
    records = db.query(model).all()

    # Check if there are any records
    if not records:
        with open(error_log_file, "a") as error_log:
            error_log.write(f"No records found in {table_name}\n")
        raise HTTPException(
            status_code=404, detail=f"No records found in {table_name}")

    record_dicts = []
    for record in records:
        record_data = {}
        for key, value in dict(record.__dict__).items():
            if key == '_sa_instance_state':
                continue
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            record_data[key] = value
        record_dicts.append(record_data)

    # Get the sample record
    sample_record = record_dicts[0]
    fields = []

    # Iterate over the sample record and determine the field types
    for key, value in sample_record.items():
        field_type = "null"
        if isinstance(value, int):
            field_type = "int"
        elif isinstance(value, str):
            field_type = "string"
        elif value is None:
            field_type = "null"
        else:
            field_type = "string"

        fields.append({"name": key, "type": ["null", field_type]})

    # Create the Avro schema
    schema = {
        "type": "record",
        "name": f"{table_name}_backup",
        "fields": fields,
    }

    # Create the filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(backup_dir, f"{table_name}_{timestamp}.avro")

    # Write the records to the file
    with open(filename, "wb") as out:
        fastavro.writer(out, schema, record_dicts)

    return filename


def create_avro_full_backup(model_list, db, backup_dir=BACKUP_DIR):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Create a temporary directory on a predefined location and name
    temp_folder = TemporaryDirectory(dir=backup_dir)
    folder_path = temp_folder.name
    print(folder_path)
    zip_filename = f"backup_all_{timestamp}.zip"
    zip_filepath = os.path.join(folder_path, zip_filename)

    avro_files = []

    for model in model_list:
        file = create_avro_backup(
            model, db, model.__tablename__, backup_dir=folder_path)
        avro_files.append(file)

    with ZipFile(zip_filepath, 'w') as zipObj:
        for file in avro_files:
            filename = os.path.basename(file)
            zipObj.write(file, arcname=filename)

    new_zip_filepath = os.path.join(backup_dir, f"{zip_filename}")
    print(zip_filepath, new_zip_filepath)
    os.rename(zip_filepath, new_zip_filepath)
    temp_folder.cleanup()
    return new_zip_filepath


def restore_table_from_avro(file, db, model, table_name, backup_dir=BACKUP_DIR):
    try:
        # Read the file
        reader = fastavro.reader(file.file)
        records = list(reader)
    except Exception as e:
        with open(error_log_file, "a") as error_log:
            error_log.write(f"Invalid AVRO file: {str(e)}\n")
        # Handle any exceptions
        raise HTTPException(
            status_code=400, detail=f"Invalid AVRO file: {str(e)}")

    # Check if the file has the expected columns
    expected_columns = model.__table__.columns.keys()
    if not records:
        with open(error_log_file, "a") as error_log:
            error_log.write(f"AVRO file has no records\n")
        raise HTTPException(
            status_code=404, detail=f"AVRO file has no records")

    first_record = records[0]
    missing_columns = [
        col for col in expected_columns if col not in first_record]

    if missing_columns:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"AVRO file is missing columns: {', '.join(missing_columns)}\n")
        raise HTTPException(
            status_code=400, detail=f"AVRO file is missing columns: {', '.join(missing_columns)}")

    try:
        # Delete all records from the table
        db.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
        db.query(model).delete()
        db.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
        db.commit()
    except Exception as e:
        db.rollback()
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"Error deleting records from {model.__tablename__}: {str(e)}\n")
        raise HTTPException(
            status_code=500, detail=f"Error deleting records from {model.__tablename__}: {str(e)}")

    # Prepare lists for successful and failed records
    successfully_inserted = []
    failed_records = []

    # Iterate over the records and insert them into the database
    for record in records:
        try:
            # Filter the record to only include columns that exist in the model
            filtered_data = {
                key: value for key, value in record.items() if key in model.__table__.columns.keys()
            }

            # Create an instance of the model with the filtered data
            db_item = model(**filtered_data)
            # Add the instance to the database
            db.add(db_item)
            db.flush()
            # Commit the transaction
            db.commit()

            # Add the filtered data to the list of successfully inserted records
            successfully_inserted.append(filtered_data)
        except Exception as e:
            # Add the filtered data and the error to the list of failed records
            failed_records.append({
                "record": filtered_data,
                "error": str(e)
            })
            # Rollback the transaction
            db.rollback()
            db.expire_all()

    if failed_records:
        with open(error_log_file, "a") as error_log:
            error_log.write(
                f"Failed to restore {len(failed_records)} records to {table_name}\n")

    return {
        "message": f"Restored {len(successfully_inserted)} records to {table_name}",
        "failed": failed_records if failed_records else None
    }


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
