# For data manipulation
import pandas as pd

# For database connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# For environment variables
import os

# For time and date management
import time
from datetime import datetime

# Models
from models import Base, Department, Job, HiredEmployee

# Database connection parameters
DB_HOST = os.getenv("MYSQL_HOST")
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD")
DB_NAME = os.getenv("MYSQL_DATABASE")

DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def connect_to_database(retries=5, delay=5):
    """
    Connects to the database using the provided parameters.
    Retries the connection if it fails.

    Args:
        retries (int): Number of retries.
        delay (int): Delay between retries in seconds.

    Returns:
        SessionLocal: SQLAlchemy session object.
    """
    for i in range(retries):
        try:
            engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(engine)
            SessionLocal = sessionmaker(bind=engine)
            print("Database connection successful.")
            return SessionLocal
        except Exception as e:
            print(f"Connection attempt {i + 1}")
            time.sleep(delay)

def get_column_names_from_model(model):
    """
    Returns a list of column names for a given model.

    Args:
        model: SQLAlchemy model class.

    Returns:
        list: List of column names.
    """
    return [column.name for column in model.__table__.columns]

def migrate_data(file_path, table_name, model, SessionLocal):
    """
    Migrates data from a CSV file to a database table, handling duplicates,
    date/time conversions, and logging failed records.
    
    Args:
        file_path (str): Path to the CSV file.
        table_name (str): Name of the database table.
        model: SQLAlchemy model class.
        SessionLocal: SQLAlchemy session object.
        max_retries (int): Maximum number of retries for database connection.
        retry_delay (int): Delay in seconds between retries.
    """
    # path to the error log file
    # This file will be created if it doesn't exist
    error_log_file = "/data/failed_registers.txt"

    if not os.path.exists(error_log_file):
        with open(error_log_file, "w") as f:
            f.write("Data migration started.\n")

    session = SessionLocal()

    try:
        # Read the CSV file
        print(f"Reading data from {file_path}")
        df = pd.read_csv(file_path, header=None)
        column_names = get_column_names_from_model(model)

        # Check if the number of columns in the CSV matches the model
        if len(df.columns) != len(column_names):
            raise ValueError(f"Number of columns in {file_path} does not match the model {table_name}")
        df.columns = column_names

        print(f"Migrating data to {table_name}")
        for index, row in df.iterrows():
            data = row.to_dict()
            try:
                # Convert datetime if present
                for key, value in data.items():
                    if 'datetime' in key.lower() and isinstance(value, str):
                        # Convert to datetime object
                        # Replace 'Z' with '+00:00' for timezone-aware datetime
                        data[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                
                # Check for NaN values
                if any(pd.isna(value) for value in data.values()):
                    raise ValueError("NaN present on register")

                # Create an instance of the model
                instance = model(**data)
                session.add(instance)

                # Commit the transaction
                session.commit()

            except IntegrityError as e: 
                # Handle duplicate entries
                session.rollback()
                print(f"Duplicate entry: {data}")
                with open(error_log_file, "a") as error_log:
                    error_log.write(f"DUPLICATE ERROR: {data}\n")
            except ValueError as e:
                # Handle invalid data
                session.rollback()
                print(f"Invalid data: {data}")
                with open(error_log_file, "a") as error_log:
                    error_log.write(f"INVALID ERROR: {data}\n")
            except Exception as e:
                # Handle any other exceptions
                session.rollback()
                print(f"Error processing row: {data}, error: {e}")
                with open(error_log_file, "a") as error_log:
                    error_log.write(f"ERROR: {data}\n")
    except Exception as e:
        # Handle any exceptions that occur during the migration process
        session.rollback() 
        print(f"Error while migrating {table_name}")
        with open(error_log_file, "a") as error_log:
            error_log.write(f"MIGRATION ERROR: {e}\n")
    finally:
        # Ensure the session is closed
        session.close() 

if __name__ == "__main__":
  # Set the path to the data files
  data_path = "data/raw"

  # Tables to migrate
  files_to_migrate = [
    {
      "file_path": os.path.join(data_path, "departments.csv"),
      "table_name": "departments",
      "model": Department,
    },
    {
      "file_path": os.path.join(data_path, "jobs.csv"),
      "table_name": "jobs",
      "model": Job,
    },
    {
      "file_path": os.path.join(data_path, "hired_employees.csv"),
      "table_name": "hired_employees",
      "model": HiredEmployee,
    }
  ]

  # Connect to the database
  session = connect_to_database()

  # Migration process
  for item in files_to_migrate:
    migrate_data(
      item["file_path"],
      item["table_name"],
      item["model"],
      session
    )
    print(f"Table {item['table_name']} migrated successfully.")
  
  print("Data migration completed successfully.")
  with open("/data/failed_registers.txt", "a") as error_log:
    error_log.write("Data migration completed successfully.\n")
