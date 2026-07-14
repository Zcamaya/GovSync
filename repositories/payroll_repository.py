import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from models.payroll_import import PayrollImport, PayrollRecord
from storage.sqlite import connect


class PayrollRepository:
    def __init__(self, database_path: str | Path | None = None):
        self.database_path = Path(database_path) if database_path is not None else None

    def _connect(self) -> sqlite3.Connection:
        return connect(self.database_path)

    def initialize_schema(self) -> None:
        connection = self._connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS payroll_imports (
                    id TEXT PRIMARY KEY,
                    employer_id TEXT NOT NULL,
                    applicable_month TEXT NOT NULL,
                    from_date TEXT NOT NULL,
                    to_date TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    client_name TEXT NOT NULL DEFAULT '',
                    employee_count INTEGER NOT NULL DEFAULT 0,
                    original_filename TEXT NOT NULL DEFAULT '',
                    file_hash TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS payroll_records (
                    id TEXT PRIMARY KEY,
                    import_id TEXT NOT NULL,
                    batchid TEXT NOT NULL DEFAULT '',
                    fdate TEXT NOT NULL DEFAULT '',
                    tdate TEXT NOT NULL DEFAULT '',
                    custid TEXT NOT NULL DEFAULT '',
                    company TEXT NOT NULL DEFAULT '',
                    emplid TEXT NOT NULL DEFAULT '',
                    lastname TEXT NOT NULL DEFAULT '',
                    firstname TEXT NOT NULL DEFAULT '',
                    middlename TEXT NOT NULL DEFAULT '',
                    suffix TEXT NOT NULL DEFAULT '',
                    birthdate TEXT NOT NULL DEFAULT '',
                    basicrate TEXT NOT NULL DEFAULT '',
                    billrate TEXT NOT NULL DEFAULT '',
                    sssno TEXT NOT NULL DEFAULT '',
                    sss TEXT NOT NULL DEFAULT '',
                    eeshare TEXT NOT NULL DEFAULT '',
                    ershare TEXT NOT NULL DEFAULT '',
                    sssrem TEXT NOT NULL DEFAULT '',
                    er TEXT NOT NULL DEFAULT '',
                    pagibigno TEXT NOT NULL DEFAULT '',
                    pagibig TEXT NOT NULL DEFAULT '',
                    pagibigrem TEXT NOT NULL DEFAULT '',
                    phealthno TEXT NOT NULL DEFAULT '',
                    phealth TEXT NOT NULL DEFAULT '',
                    phealthrem TEXT NOT NULL DEFAULT '',
                    sssloan TEXT NOT NULL DEFAULT '',
                    pbigloan TEXT NOT NULL DEFAULT '',
                    ctr TEXT NOT NULL DEFAULT '',
                    tinno TEXT NOT NULL DEFAULT '',
                    datehired TEXT NOT NULL DEFAULT '',
                    companyid TEXT NOT NULL DEFAULT '',
                    position TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(import_id) REFERENCES payroll_imports(id) ON DELETE CASCADE
                );
                """
            )
            connection.commit()
        finally:
            connection.close()

    def file_hash(self, file_path: str | Path) -> str:
        digest = hashlib.sha256()
        with open(file_path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def get_import_by_hash(self, file_hash: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM payroll_imports WHERE file_hash = ?",
                (file_hash,),
            ).fetchone()
        finally:
            connection.close()
        return dict(row) if row is not None else None

    def get_payroll_import(self, employer_id: str, applicable_month: str, from_date: str, to_date: str, client_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT * FROM payroll_imports
                WHERE employer_id = ?
                  AND applicable_month = ?
                  AND from_date = ?
                  AND to_date = ?
                  AND client_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (employer_id, applicable_month, from_date, to_date, client_id),
            ).fetchone()
        finally:
            connection.close()
        return dict(row) if row is not None else None

    def get_payroll_import_for_month(self, employer_id: str, applicable_month: str, client_id: str) -> dict[str, Any] | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """
                SELECT * FROM payroll_imports
                WHERE employer_id = ?
                  AND applicable_month = ?
                  AND client_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (employer_id, applicable_month, client_id),
            ).fetchone()
        finally:
            connection.close()
        return dict(row) if row is not None else None

    def save_import(self, import_data: PayrollImport) -> None:
        connection = self._connect()
        try:
            connection.execute(
                """
                INSERT INTO payroll_imports (
                    id, employer_id, applicable_month, from_date, to_date, client_id,
                    client_name, employee_count, original_filename, file_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    employer_id = excluded.employer_id,
                    applicable_month = excluded.applicable_month,
                    from_date = excluded.from_date,
                    to_date = excluded.to_date,
                    client_id = excluded.client_id,
                    client_name = excluded.client_name,
                    employee_count = excluded.employee_count,
                    original_filename = excluded.original_filename,
                    file_hash = excluded.file_hash,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    import_data.id,
                    import_data.employer_id,
                    import_data.applicable_month,
                    import_data.from_date,
                    import_data.to_date,
                    import_data.client_id,
                    import_data.client_name,
                    import_data.employee_count,
                    import_data.original_filename,
                    import_data.file_hash,
                    import_data.created_at or "",
                    import_data.updated_at or "",
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def delete_import(self, import_id: str) -> None:
        connection = self._connect()
        try:
            connection.execute("DELETE FROM payroll_records WHERE import_id = ?", (import_id,))
            connection.execute("DELETE FROM payroll_imports WHERE id = ?", (import_id,))
            connection.commit()
        finally:
            connection.close()

    def _payroll_record_columns(self) -> list[str]:
        return [
            "id",
            "import_id",
            "batchid",
            "fdate",
            "tdate",
            "custid",
            "company",
            "emplid",
            "lastname",
            "firstname",
            "middlename",
            "suffix",
            "birthdate",
            "basicrate",
            "billrate",
            "sssno",
            "sss",
            "eeshare",
            "ershare",
            "sssrem",
            "er",
            "pagibigno",
            "pagibig",
            "pagibigrem",
            "phealthno",
            "phealth",
            "phealthrem",
            "sssloan",
            "pbigloan",
            "ctr",
            "tinno",
            "datehired",
            "companyid",
            "position",
        ]

    def replace_import(self, import_data: PayrollImport, records: list[dict[str, Any]]) -> None:
        connection = self._connect()
        try:
            connection.execute("DELETE FROM payroll_records WHERE import_id = ?", (import_data.id,))
            connection.execute(
                "DELETE FROM payroll_imports WHERE id = ?",
                (import_data.id,),
            )
            connection.execute(
                """
                INSERT INTO payroll_imports (
                    id, employer_id, applicable_month, from_date, to_date, client_id,
                    client_name, employee_count, original_filename, file_hash, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    import_data.id,
                    import_data.employer_id,
                    import_data.applicable_month,
                    import_data.from_date,
                    import_data.to_date,
                    import_data.client_id,
                    import_data.client_name,
                    import_data.employee_count,
                    import_data.original_filename,
                    import_data.file_hash,
                    import_data.created_at or "",
                    import_data.updated_at or "",
                ),
            )
            import_id = import_data.id
            columns = self._payroll_record_columns()
            placeholders = ", ".join("?" for _ in columns)
            for record in records:
                record_id = str(record.get("id") or uuid.uuid4())
                values = [record_id, import_id]
                for column in columns[2:]:
                    values.append(str(record.get(column, "")))
                connection.execute(
                    f"INSERT INTO payroll_records ({', '.join(columns)}) VALUES ({placeholders})",
                    values,
                )
            connection.commit()
        finally:
            connection.close()
