from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
import requests
import secrets
import os

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)

API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")


@app.route('/')
def index():
    return render_template('index.html', title='Globant Data Engineer Challenge')


@app.route('/create')
def create():
    return render_template('create.html', title='Create')


@app.route('/create/department', methods=['GET', 'POST'])
def create_department():
    if request.method == 'POST':
        # Split the department titles by commas and remove any leading or trailing whitespace

        print(request.form)

        department_titles = [title.strip()
                             for title in request.form['department_title'].split(',')]
        print("Received department titles:", department_titles)

        # Preparing array of dicts for the POST request
        data = []
        for department_title in department_titles:
            data.append({"department": department_title})

        # Sending the POST request
        response = requests.post(
            f"http://{API_USER}:{API_PASS}@localhost:8000/departments",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            flash("Jobs created successfully!", "success_dept")
            # Vuelve a la página de creación
            return redirect(url_for('create'))
        else:
            flash("Error creating department", "error_dept")
            # Vuelve a la página de creación
            return redirect(url_for('create'))


@app.route('/create/job', methods=['GET', 'POST'])
def create_job():
    if request.method == 'POST':
        # Split the job titles by commas and remove any leading or trailing whitespace

        job_titles = [title.strip()
                      for title in request.form['job_title'].split(',')]
        print("Received job titles:", job_titles)

        # Preparing array of dicts for the POST request
        data = []
        for job_title in job_titles:
            data.append({"job": job_title})

        # Sending the POST request
        response = requests.post(
            f"http://{API_USER}:{API_PASS}@localhost:8000/jobs",
            json=data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            flash("Jobs created successfully!", "success_job")
            # Vuelve a la página de creación
            return redirect(url_for('create'))
        else:
            flash("Error creating jobs", "error")
            # Vuelve a la página de creación
            return redirect(url_for('create'))


@app.route('/create/employee', methods=['GET', 'POST'])
def create_employee():
    if request.method == 'POST':
        request_data = request.form.to_dict()
        # Split job_ids by commas and remove any leading or trailing whitespace
        job_ids = [id.strip() for id in request_data['job_ids'].split(',')]
        # Split department_ids by commas and remove any leading or trailing whitespace
        department_ids = [id.strip()
                          for id in request_data['department_ids'].split(',')]
        # Split names by commas and remove any leading or trailing whitespace
        names = [name.strip() for name in request_data['names'].split(',')]
        # Check if job_ids and, department_ids adn names have the same length
        if len(job_ids) != len(department_ids) or len(job_ids) != len(names):
            flash(
                "Job IDs, Department IDs, and Names must have the same length", "error_emp")
            return redirect(url_for('create'))
        else:
            # Checking if all items in job_ids, department_ids are integers
            for id in job_ids:
                if not id.isdigit():
                    flash("All items in Job IDs must be integers", "error_emp")
                    return redirect(url_for('create'))
            for id in department_ids:
                if not id.isdigit():
                    flash("All items in Department IDs must be integers", "error_emp")
                    return redirect(url_for('create'))
            # Preparing array of dicts for the POST request
            data = []
            # Datetime in the format YYYY-MM-DD HH:MM:SS
            actual_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for name, job_id, department_id in zip(names, job_ids, department_ids):
                data.append({"name": name, "job_id": job_id,
                            "department_id": department_id, "datetime": actual_datetime})
            # Sending the POST request
            response = requests.post(
                f"http://{API_USER}:{API_PASS}@localhost:8000/employees",
                json=data,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                flash("Employees created successfully!", "success_emp")
                # Vuelve a la página de creación
                return redirect(url_for('create'))
    return redirect(url_for('create'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
