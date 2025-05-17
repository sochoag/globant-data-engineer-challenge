# Using python:3.14-slim as the base image for a lightweight Python environment
FROM python:3.10
WORKDIR /app
COPY /app/requirements.txt .
RUN pip install -r requirements.txt
COPY /app/src/ ./src