import requests
from flask import flash, redirect, url_for
from datetime import datetime
import os

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")
API_HOST = os.getenv("API_HOST")


def create_departments(form_data):
    department_titles = [title.strip()
                         for title in form_data['department_title'].split(',')]

    data = [{"department": dept} for dept in department_titles]

    response = requests.post(
        f"http://{API_USER}:{API_PASS}@{API_HOST}:8000/departments",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        flash("Departments created successfully!", "success_dept")
    else:
        flash("Error creating departments", "error_dept")

    return redirect(url_for('create'))


def create_jobs(form_data):
    job_titles = [title.strip() for title in form_data['job_title'].split(',')]

    data = [{"job": job} for job in job_titles]

    response = requests.post(
        f"http://{API_USER}:{API_PASS}@{API_HOST}:8000/jobs",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        flash("Jobs created successfully!", "success_job")
    else:
        flash("Error creating jobs", "error_job")

    return redirect(url_for('create'))


def create_employees(form_data):
    job_ids = [id.strip() for id in form_data['job_ids'].split(',')]
    department_ids = [id.strip()
                      for id in form_data['department_ids'].split(',')]
    names = [name.strip() for name in form_data['names'].split(',')]

    if len(job_ids) != len(department_ids) or len(job_ids) != len(names):
        flash("Job IDs, Department IDs, and Names must have the same length", "error_emp")
        return redirect(url_for('create'))

    for id_list, field_name in [(job_ids, "Job IDs"), (department_ids, "Department IDs")]:
        for item in id_list:
            if not item.isdigit():
                flash(
                    f"All items in {field_name} must be integers", "error_emp")
                return redirect(url_for('create'))

    actual_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = [
        {"name": name, "job_id": job_id,
            "department_id": dept_id, "datetime": actual_datetime}
        for name, job_id, dept_id in zip(names, job_ids, department_ids)
    ]

    response = requests.post(
        f"http://{API_USER}:{API_PASS}@{API_HOST}:8000/employees",
        json=data,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        flash("Employees created successfully!", "success_emp")
    else:
        flash("Error creating employees", "error_emp")

    return redirect(url_for('create'))
