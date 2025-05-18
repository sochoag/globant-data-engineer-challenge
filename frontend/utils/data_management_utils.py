import requests
from flask import flash, redirect, url_for, Response
import os


API_USER = os.getenv("API_USER")
API_PASS = os.getenv("API_PASS")
API_HOST = os.getenv("API_HOST")


def backup(endpoint):
    url = f"http://{API_USER}:{API_PASS}@{API_HOST}:8000/avro/backup/{endpoint}"
    print(url)
    try:
        respones = requests.get(url)
        headers = [(name, value)
                   for (name, value) in respones.raw.headers.items()]
        return Response(respones.content, headers=headers, status=respones.status_code)
    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect(url_for('data'))


def restore(endpoint, file):
    url = f"http://{API_USER}:{API_PASS}@{API_HOST}:8000/avro/restore/{endpoint}"

    try:
        # Preparar archivo para requests
        files = {'file': (file.filename, file.stream, file.mimetype)}

        # Enviar solicitud POST a la API
        resp = requests.post(url, files=files)

        # Reenviar respuesta al cliente
        headers = [(name, value) for (name, value) in resp.raw.headers.items()]
        # Printing the response details
        print(resp.status_code)
        if resp.status_code == 200:
            flash(f"Restored {file.filename}", "success_restore")
        else:
            flash(
                f"Error restoring {file.filename}: {resp.text}", "error_restore")
        return redirect(url_for('data'))

    except Exception as e:
        flash(f"Error during restore: {str(e)}", "error_restore")
    return redirect(url_for('data'))
