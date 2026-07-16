from pathlib import Path
from typing import Any

from storage.sqlite import connect


class EmployeeRecordsRepository:
    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(database_path) if database_path is not None else None

    def _connect(self):
        return connect(self.database_path)

    def get_statistics(self, employer_id: str | None = None) -> dict[str, Any]:
        connection = self._connect()
        try:
            employer_filter = "WHERE employer_id = ?" if employer_id else ""
            params: list[Any] = [employer_id] if employer_id else []

            # Count unique employees grouped by employer and company (column E)
            employee_query = f"""
                SELECT COUNT(*) AS total_employees FROM (
                    SELECT
                        CASE
                            WHEN trim(pr.emplid) <> '' THEN trim(pr.emplid)
                            ELSE trim(pr.lastname) || '|' || trim(pr.firstname) || '|' || trim(pr.birthdate) || '|' || trim(pr.company)
                        END AS employee_key,
                        pr.company
                    FROM payroll_records pr
                    JOIN payroll_imports pi ON pi.id = pr.import_id
                    {employer_filter}
                    GROUP BY employee_key, pr.company
                )
            """
            client_query = f"""
                SELECT COUNT(DISTINCT client_name) AS total_clients
                FROM payroll_imports
                {employer_filter}
            """
            import_query = f"""
                SELECT COUNT(*) AS total_imports
                FROM payroll_imports
                {employer_filter}
            """
            latest_query = f"""
                SELECT created_at FROM payroll_imports
                {employer_filter}
                ORDER BY created_at DESC, id DESC
                LIMIT 1
            """

            total_employees = connection.execute(employee_query, params).fetchone()["total_employees"]
            total_clients = connection.execute(client_query, params).fetchone()["total_clients"]
            total_imports = connection.execute(import_query, params).fetchone()["total_imports"]
            latest_row = connection.execute(latest_query, params).fetchone()
            last_imported = latest_row["created_at"] if latest_row else ""

            return {
                "total_employees": int(total_employees or 0),
                "total_clients": int(total_clients or 0),
                "total_imports": int(total_imports or 0),
                "last_imported": str(last_imported or ""),
            }
        finally:
            connection.close()

    def get_filter_options(self, employer_id: str | None = None) -> dict[str, list[str]]:
        connection = self._connect()
        try:
            params: list[Any] = [employer_id] if employer_id else []
            # Use distinct company values from payroll_records (column E) for client filter
            clients = connection.execute(
                f"""
                SELECT DISTINCT pr.company AS value
                FROM payroll_records pr
                JOIN payroll_imports pi ON pi.id = pr.import_id
                {"WHERE pi.employer_id = ?" if employer_id else ""}
                ORDER BY value
                """,
                params,
            ).fetchall()
            
            # Get applicable months
            months = connection.execute(
                f"""
                SELECT DISTINCT pi.applicable_month AS value
                FROM payroll_imports pi
                WHERE {"pi.employer_id = ? AND " if employer_id else ""}trim(pi.applicable_month) <> ''
                ORDER BY pi.created_at DESC
                """,
                params,
            ).fetchall()
            
            # Get distinct last names
            lastnames = connection.execute(
                f"""
                SELECT DISTINCT pr.lastname AS value
                FROM payroll_records pr
                JOIN payroll_imports pi ON pi.id = pr.import_id
                WHERE {"pi.employer_id = ? AND " if employer_id else ""}trim(pr.lastname) <> ''
                ORDER BY value
                """,
                params,
            ).fetchall()
            
            employers = connection.execute(
                """
                SELECT DISTINCT employer_id AS value
                FROM payroll_imports
                WHERE trim(employer_id) <> ''
                ORDER BY value
                """
            ).fetchall()
            return {
                "clients": [row["value"] for row in clients if row["value"]],
                "applicable_months": [row["value"] for row in months if row["value"]],
                "lastnames": [row["value"] for row in lastnames if row["value"]],
                "employers": [row["value"] for row in employers if row["value"]],
            }
        finally:
            connection.close()

    def list_employees(
        self,
        employer_id: str | None,
        search_text: str = "",
        client_filter: str = "",
        applicable_month_filter: str = "",
        lastname_filter: str = "",
        employer_filter: str = "",
        sort_by: str = "lastname",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        connection = self._connect()
        try:
            where_clauses: list[str] = []
            params: list[Any] = []

            if employer_filter:
                where_clauses.append("pi.employer_id = ?")
                params.append(employer_filter)

            if search_text:
                search_value = f"%{search_text.lower()}%"
                where_clauses.append(
                    """
                    (
                        lower(coalesce(pr.emplid, '')) LIKE ?
                        OR lower(coalesce(pr.lastname, '')) LIKE ?
                        OR lower(coalesce(pr.firstname, '')) LIKE ?
                        OR lower(coalesce(pr.lastname, '') || ' ' || coalesce(pr.firstname, '')) LIKE ?
                        OR lower(coalesce(pr.sssno, '')) LIKE ?
                        OR lower(coalesce(pr.pagibigno, '')) LIKE ?
                        OR lower(coalesce(pr.phealthno, '')) LIKE ?
                        OR lower(coalesce(pr.tinno, '')) LIKE ?
                    )
                    """
                )
                params.extend([search_value] * 8)

            if client_filter:
                where_clauses.append("lower(coalesce(pr.company, '')) = ?")
                params.append(client_filter.lower())

            if applicable_month_filter:
                where_clauses.append("lower(coalesce(pi.applicable_month, '')) = ?")
                params.append(applicable_month_filter.lower())

            if lastname_filter:
                where_clauses.append("lower(coalesce(pr.lastname, '')) = ?")
                params.append(lastname_filter.lower())

            base_where = " AND ".join(where_clauses) if where_clauses else "1=1"
            # Return one row per unique employee per company (company == column E in earnings)
            sql = f"""
                WITH ranked AS (
                    SELECT
                        CASE
                            WHEN trim(pr.emplid) <> '' THEN trim(pr.emplid)
                            ELSE trim(pr.lastname) || '|' || trim(pr.firstname) || '|' || trim(pr.birthdate) || '|' || trim(pr.company)
                        END AS employee_key,
                        pi.employer_id,
                        pr.emplid,
                        pr.lastname,
                        pr.firstname,
                        pr.middlename,
                        pr.suffix,
                        pr.birthdate,
                        pr.sssno,
                        pr.pagibigno,
                        pr.phealthno,
                        pr.tinno,
                        pr.datehired,
                        pr.position,
                        pr.company AS client_name,
                        pr.basicrate,
                        pr.billrate,
                        pr.sss,
                        pr.eeshare,
                        pr.ershare,
                        pr.pagibig,
                        pr.phealth,
                        pr.sssloan,
                        pr.pbigloan,
                        pr.ctr,
                        pi.applicable_month,
                        pi.from_date,
                        pi.to_date,
                        pi.created_at,
                        ROW_NUMBER() OVER (
                            PARTITION BY
                                CASE
                                    WHEN trim(pr.emplid) <> '' THEN trim(pr.emplid)
                                    ELSE trim(pr.lastname) || '|' || trim(pr.firstname) || '|' || trim(pr.birthdate) || '|' || trim(pr.company)
                                END,
                                pr.company
                            ORDER BY pi.created_at DESC, pi.from_date DESC, pi.to_date DESC, pr.lastname DESC, pr.firstname DESC
                        ) AS rn
                    FROM payroll_records pr
                    JOIN payroll_imports pi ON pi.id = pr.import_id
                    WHERE {base_where}
                )
                SELECT * FROM ranked WHERE rn = 1
            """
            total_count_row = connection.execute(f"SELECT COUNT(*) AS total_count FROM ({sql})", params).fetchone()
            total_count = int(total_count_row["total_count"] or 0)

            order_map = {
                "employee_id": "emplid",
                "lastname": "lastname",
                "firstname": "firstname",
                "client": "client_name",
                "position": "position",
                "date_hired": "datehired",
                "latest_payroll": "created_at",
            }
            sort_column = order_map.get(sort_by, "lastname")
            sort_direction = "DESC" if str(sort_order).lower() == "desc" else "ASC"
            sql += f" ORDER BY {sort_column} {sort_direction}, lastname ASC, firstname ASC"
            sql += " LIMIT ? OFFSET ?"
            params.extend([page_size, (page - 1) * page_size])

            rows = connection.execute(sql, params).fetchall()
            results = []
            for row in rows:
                results.append(
                    {
                        "employee_key": row["employee_key"],
                        "employer_id": row["employer_id"],
                        "employee_id": row["emplid"],
                        "lastname": row["lastname"],
                        "firstname": row["firstname"],
                        "middlename": row["middlename"],
                        "suffix": row["suffix"],
                        "birthdate": row["birthdate"],
                        "client": row["client_name"],
                        "position": row["position"],
                        "sss_number": row["sssno"],
                        "philhealth_number": row["phealthno"],
                        "pagibig_number": row["pagibigno"],
                        "date_hired": row["datehired"],
                        "latest_payroll_period": self._format_payroll_period(row["applicable_month"], row["from_date"], row["to_date"]),
                        "basic_rate": row["basicrate"],
                        "billing_rate": row["billrate"],
                        "sss": row["sss"],
                        "employee_share": row["eeshare"],
                        "employer_share": row["ershare"],
                        "pagibig": row["pagibig"],
                        "philhealth": row["phealth"],
                        "sss_loan": row["sssloan"],
                        "pagibig_loan": row["pbigloan"],
                        "ctr": row["ctr"],
                        "tin_number": row["tinno"],
                    }
                )
            return results, total_count
        finally:
            connection.close()

    def get_employee_payroll_history(self, employer_id: str | None, employee_id: str = "", sss_number: str = "") -> list[dict[str, Any]]:
        connection = self._connect()
        try:

            # If employer_id is numeric or doesn't look like a company name, ignore it and use no filter
            # (The employer_id from the UI might be numeric but the database stores employer names)
            use_employer_filter = employer_id and isinstance(employer_id, str) and employer_id.strip() and not str(employer_id).isdigit()
            
            if use_employer_filter:
                rows = connection.execute(
                    """
                    SELECT
                        pi.applicable_month,
                        pi.from_date,
                        pi.to_date,
                        pi.client_name,
                        pr.basicrate,
                        pr.sss,
                        pr.pagibig,
                        pr.phealth,
                        pr.sssloan,
                        pr.pbigloan,
                        pr.emplid,
                        pr.sssno,
                        pr.lastname,
                        pr.firstname,
                        pr.birthdate,
                        pr.company
                    FROM payroll_records pr
                    JOIN payroll_imports pi ON pi.id = pr.import_id
                    WHERE pi.employer_id = ?
                      AND trim(pr.emplid) = ?
                      AND trim(pr.sssno) = ?
                    ORDER BY pi.created_at DESC, pi.from_date DESC, pi.to_date DESC
                    """,
                    (employer_id, employee_id, sss_number),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT
                        pi.applicable_month,
                        pi.from_date,
                        pi.to_date,
                        pi.client_name,
                        pr.basicrate,
                        pr.sss,
                        pr.pagibig,
                        pr.phealth,
                        pr.sssloan,
                        pr.pbigloan,
                        pr.emplid,
                        pr.sssno,
                        pr.lastname,
                        pr.firstname,
                        pr.birthdate,
                        pr.company
                    FROM payroll_records pr
                    JOIN payroll_imports pi ON pi.id = pr.import_id
                    WHERE trim(pr.emplid) = ?
                      AND trim(pr.sssno) = ?
                    ORDER BY pi.created_at DESC, pi.from_date DESC, pi.to_date DESC
                    """,
                    (employee_id, sss_number),
                ).fetchall()

            results = []
            for row in rows:
                results.append(
                    {
                        "applicable_month": row["applicable_month"],
                        "from_date": row["from_date"],
                        "to_date": row["to_date"],
                        "client": row["client_name"],
                        "company": row["company"],
                        "basic_rate": row["basicrate"],
                        "sss": row["sss"],
                        "sss_number": row["sssno"],
                        "pagibig": row["pagibig"],
                        "philhealth": row["phealth"],
                        "sss_loan": row["sssloan"],
                        "pagibig_loan": row["pbigloan"],
                        "employee_id": row["emplid"],
                    }
                )
            return results
        finally:
            connection.close()

    def _format_payroll_period(self, applicable_month: str, from_date: str, to_date: str) -> str:
        if applicable_month:
            return str(applicable_month)
        if from_date and to_date:
            return f"{from_date} - {to_date}"
        return "-"
