# 📁 Globant Data Engineer Challenge

This project solves the technical challenge from Globant by implementing:

- Migration of historical data from **CSV files** to a relational database (MySQL)
- A **RESTful API service** for inserting new transactions (up to 1000 rows per request)
- **Backup and restore functionality** for each table in **AVRO format**



---

## ✅ Features

1. **Migrate historical data** from CSV files to MySQL  
2. **REST API Service**
   - Accepts batch inserts (1–1000 rows)
   - Validates input against data dictionary rules
3. **AVRO backup system**
   - Each table can be backed up into `.avro` files
   - All tables can be exported into a ZIP file containing all backups
4. **Restore feature**
   - Restore any table from its corresponding AVRO file
5. **Basic authentication**
   - Protects sensitive endpoints using username/password

---

## 🧱 Folder Structure
```sh
globant-data-engineer-challenge/
├── .env
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile.app
├── Dockerfile.migration
│
├── app/
│ ├── requirements.txt
│ └── src/
│ ├── database.py
│ ├── main.py
│ │
│ ├── api/
│ │ ├── api_utils.py
│ │ ├── endpoints.py
│ │
│ ├── avro/
│ │ ├── avro_utils.py
│ │ ├── endpoints.py
│ │
│ ├── models/
│ │ ├── department.py
│ │ ├── employee.py
│ │ ├── job.py
│ │ └── init .py
│ │
│ └── schemas/
│ ├── department.py
│ ├── employee.py
│ ├── job.py
│ └── init .py
│
└── data_migration/
├── requirements.txt
└── src/
├── main.py
├── models.py
└── data/
└── raw/
├── departments.csv
├── jobs.csv
└── hired_employees.csv
```
---

## 🚀 Getting Started

### 🔧 Requirements

- Docker & Docker Compose

### 🐳 Run Everything with Docker

To start the full system:

```bash
docker-compose up
```
This will:

1. Start a MySQL database
2. Run the data migration script (loads CSV files into MySQL)
3. Launch the FastAPI service
4. Expose the API on port 8000

🗃️ Database Schema

|Table|Fields|
|-----|------|
|departments|id *(auto generated)*, department|
|jobs|id *(auto generated)*, job|
|hired_employees|id *(auto generated)*, name, datetime, department_id, job_id|

---
### 📤 Migrating Historical Data (CSV → MySQL)
A Python script is included that imports the CSV files into the database. This runs automatically via the migration service defined in docker-compose.yml.

### 🌐 REST API Endpoints
Built with FastAPI , the service offers the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /departments | Creates a new department |
| POST   | /jobs | Creates a new job|
| POST   | /employees | Creates a new employee|

* Supports batch inserts (1–1000 rows)
* Validates each record against the data dictionary rules
* Returns a JSON response with the success/failed records

---
### 💾 Backup Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /avro/backup/departments | Backup the departments table |
| GET    | /avro/backup/jobs | Backup the jobs table |
| GET    | /avro/backup/employees | Backup the employees table |
| GET    | /avro/backup/all | Backup of all tables in the database |

> The response is a ZIP file or a AVRO file containing the backup

### 🔁 Restore Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /avro/restore/departments | Restore the departments table |
| POST   | /avro/restore/jobs | Restore the jobs table |
| POST   | /avro/restore/employees | Restore the employees table |

> The request body should contain the file to be restored

### 🔒 Security
The API protects critical endpoints using HTTP Basic Authentication .

#### Credentials
Defined in environment variables:
```env
API_USER=admin
API_PASS=adminpass123
```

### Environment Variables
Example environment variables:
```env
MYSQL_HOST=db
MYSQL_USER=root
MYSQL_PASSWORD=rootpass123
MYSQL_DATABASE=globant

API_USER=admin
API_PASS=adminpass123
```
