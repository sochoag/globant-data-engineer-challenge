import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os

API_HOST = os.getenv("API_HOST")


def generate_report_data():

    quarterly_url = f"http://{API_HOST}:8000/report/quarterly_hires"
    above_avg_url = f"http://{API_HOST}:8000/report/departments_above_average"

    try:
        # Llamadas a los endpoints
        quarterly_data = requests.get(quarterly_url).json().get("data", [])
        above_avg_data = requests.get(above_avg_url).json().get("data", [])

        # Convertir a DataFrame
        df_quarterly = pd.DataFrame(quarterly_data)
        df_above_avg = pd.DataFrame(above_avg_data)

        # Ordenar datos
        df_quarterly.sort_values(by=["department", "job"], inplace=True)
        df_above_avg.sort_values(by="hired", ascending=False, inplace=True)

        # Mantener copia original para mostrar en tabla
        df_quarterly_original = df_quarterly.copy()

        # Transformar datos para gráfico (formato largo)
        df_quarterly_melted = df_quarterly.melt(
            id_vars=["department", "job"],
            value_vars=["Q1", "Q2", "Q3", "Q4"],
            var_name="Quarter",
            value_name="Hires"
        )

        # Gráfico actualizado: Hires vs Quarter
        fig1 = px.bar(
            df_quarterly_melted,
            x='Quarter',
            y='Hires',
            color='job',
            facet_col='department',
            facet_col_wrap=3,
            title="Hires by Quarter per Department and Job",
            labels={"Hires": "Number of Hires", "Quarter": "Fiscal Quarter"},
            height=800
        )

        fig1.update_layout(showlegend=False)

        fig1.for_each_annotation(lambda a: a.update(
            text=a.text.split("=")[-1]))  # Limpiar título de facetas

        chart1 = pio.to_html(fig1, full_html=False)

        # Gráfico 2: Departamentos por encima del promedio
        fig2 = px.bar(
            df_above_avg,
            x='department',
            y='hired',
            title="Departments Above Average Hiring",
            labels={"hired": "Employees Hired", "department": "Department"}
        )
        chart2 = pio.to_html(fig2, full_html=False)

        return {
            "success": True,
            "chart1": chart1,
            "chart2": chart2,
            "quarterly_data": df_quarterly_original.to_dict(orient="records"),
            "above_avg_data": df_above_avg.to_dict(orient="records")
        }

    except Exception as e:
        print("Error generating reports:", e)
        return {
            "success": False,
            "chart1": "<p>Error loading chart.</p>",
            "chart2": "<p>Error loading chart.</p>",
            "quarterly_data": [],
            "above_avg_data": []
        }
