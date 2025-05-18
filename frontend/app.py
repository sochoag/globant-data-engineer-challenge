# app.py

from flask import Flask, render_template, request, flash, redirect, url_for
import secrets
import os

# Importar funciones desde el módulo utils/create_utils.py
from utils.create_utils import create_departments, create_jobs, create_employees
from utils.data_management_utils import backup, restore

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)


@app.route('/')
def index():
    return render_template('index.html', title='Globant Data Engineer Challenge')


@app.route('/create')
def create():
    return render_template('create.html', title='Create')


@app.route('/create/department', methods=['GET', 'POST'])
def handle_create_department():
    if request.method == 'POST':
        return create_departments(request.form)
    return render_template('create_department.html', title='Create Department')


@app.route('/create/job', methods=['GET', 'POST'])
def handle_create_job():
    if request.method == 'POST':
        return create_jobs(request.form)
    return render_template('create_job.html', title='Create Job')


@app.route('/create/employee', methods=['GET', 'POST'])
def handle_create_employee():
    if request.method == 'POST':
        return create_employees(request.form)
    return render_template('create_employee.html', title='Create Employee')


@app.route('/data')
def data():
    return render_template('data_management.html', title='Data Management')


@app.route('/data/backup/departments')
def backup_departments():
    return backup('departments')


@app.route('/data/backup/jobs')
def backup_jobs():
    return backup('jobs')


@app.route('/data/backup/employees')
def backup_employees():
    return backup('employees')


@app.route('/data/backup/all')
def backup_all():
    return backup('all')


@app.route('/data/restore/departments', methods=['POST'])
def restore_departments():
    return restore('departments', request.files['file'])


@app.route('/data/restore/jobs', methods=['POST'])
def restore_jobs():
    return restore('jobs', request.files['file'])


@app.route('/data/restore/employees', methods=['POST'])
def restore_employees():
    return restore('employees', request.files['file'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
