from sqlalchemy import text


def get_quarterly_hires(db):
    query = text(
        """
            WITH HiresWithQuartil AS (
                SELECT
                    he.department_id,
                    he.job_id,
                    CASE
                        WHEN MONTH(he.`datetime`) BETWEEN '01' AND '03' THEN 1
                        WHEN MONTH(he.`datetime`) BETWEEN '04' AND '06' THEN 2
                        WHEN MONTH(he.`datetime`) BETWEEN '07' AND '09' THEN 3
                        WHEN MONTH(he.`datetime`) BETWEEN '10' AND '12' THEN 4
                        ELSE NULL
                    END AS quartil
                FROM hired_employees he
                WHERE YEAR(he.`datetime`) = '2021'
            )
            SELECT
                d.department,
                j.job,
                COUNT(CASE WHEN hwq.quartil = 1 THEN 1 END) AS Q1,
                COUNT(CASE WHEN hwq.quartil = 2 THEN 1 END) AS Q2,
                COUNT(CASE WHEN hwq.quartil = 3 THEN 1 END) AS Q3,
                COUNT(CASE WHEN hwq.quartil = 4 THEN 1 END) AS Q4
            FROM HiresWithQuartil hwq
            LEFT JOIN departments d ON hwq.department_id = d.id
            LEFT JOIN jobs j ON hwq.job_id = j.id
            GROUP BY d.department, j.job
            ORDER BY d.department ASC, j.job ASC;
        """
    )

    result = db.execute(query).fetchall()

    return [
        {"department": row[0], "job": row[1], "Q1": row[2],
            "Q2": row[3], "Q3": row[4], "Q4": row[5]}
        for row in result
    ]


def get_departments_above_average(db):
    query = text(
        """
            WITH DepartmentHires AS (
                SELECT 
                    department_id,
                    COUNT(id) as num_hired
                FROM hired_employees
                WHERE YEAR(`datetime`) = "2021"
                GROUP BY department_id
            ),
            AverageHires AS (
                SELECT AVG(num_hired) as avg_hired
                FROM DepartmentHires
            )

            SELECT d.id, d.department, dh.num_hired as hired
            FROM departments d 
            JOIN DepartmentHires dh ON d.id = dh.department_id
            JOIN AverageHires ah ON dh.num_hired > ah.avg_hired
            ORDER BY dh.num_hired DESC
        """
    )

    result = db.execute(query).fetchall()

    return [
        {"id": row[0], "department": row[1], "hired": row[2]} for row in result
    ]
