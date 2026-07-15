from pathlib import Path

from models.employer import Employer
from storage.sqlite import connect, initialize_database


class EmployerRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def _row_to_employer(self, row) -> Employer:
        return Employer(
            id=row["id"],
            name=row["name"],
            address=row["address"],
            tin=row["tin"],
            sss_number=row["sss_number"],
            philhealth_number=row["philhealth_number"],
            hdmf_number=row["hdmf_number"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_by_id(self, employer_id: int) -> Employer | None:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT * FROM employers WHERE id = ?",
                (employer_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return self._row_to_employer(row)

    def get_by_name(self, name: str) -> Employer | None:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT * FROM employers WHERE lower(trim(name)) = lower(trim(?))",
                (name,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return self._row_to_employer(row)

    def list_all(self, include_inactive: bool = True) -> list[Employer]:
        connection = connect(self.database_path)
        try:
            query = "SELECT * FROM employers"
            if not include_inactive:
                query += " WHERE status = 'active'"
            query += " ORDER BY name COLLATE NOCASE"
            rows = connection.execute(query).fetchall()
        finally:
            connection.close()
        return [self._row_to_employer(row) for row in rows]

    def list_active(self) -> list[Employer]:
        return self.list_all(include_inactive=False)

    def count_accounts(self, employer_id: int) -> int:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM accounts WHERE employer_id = ?",
                (employer_id,),
            ).fetchone()
        finally:
            connection.close()
        return int(row["total"]) if row is not None else 0

    def save(self, employer: Employer) -> Employer:
        connection = connect(self.database_path)
        try:
            if employer.id is None:
                cursor = connection.execute(
                    """
                    INSERT INTO employers (
                        name, address, tin, sss_number, philhealth_number, hdmf_number, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        employer.name.strip(),
                        employer.address.strip(),
                        employer.tin.strip(),
                        employer.sss_number,
                        employer.philhealth_number,
                        employer.hdmf_number,
                        employer.status,
                    ),
                )
                employer_id = cursor.lastrowid
            else:
                connection.execute(
                    """
                    UPDATE employers SET
                        name = ?,
                        address = ?,
                        tin = ?,
                        sss_number = ?,
                        philhealth_number = ?,
                        hdmf_number = ?,
                        status = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        employer.name.strip(),
                        employer.address.strip(),
                        employer.tin.strip(),
                        employer.sss_number,
                        employer.philhealth_number,
                        employer.hdmf_number,
                        employer.status,
                        employer.id,
                    ),
                )
                employer_id = employer.id
            connection.commit()
        finally:
            connection.close()
        return self.get_by_id(int(employer_id)) or employer

    def delete_by_id(self, employer_id: int) -> None:
        connection = connect(self.database_path)
        try:
            connection.execute("DELETE FROM employers WHERE id = ?", (employer_id,))
            connection.commit()
        finally:
            connection.close()

    def find_matching(
        self,
        name: str,
        sss_number: str = "",
        philhealth_number: str = "",
        hdmf_number: str = "",
    ) -> Employer | None:
        connection = connect(self.database_path)
        try:
            row = connection.execute(
                """
                SELECT * FROM employers
                WHERE lower(trim(name)) = lower(trim(?))
                  AND sss_number = ?
                  AND philhealth_number = ?
                  AND hdmf_number = ?
                LIMIT 1
                """,
                (name, sss_number, philhealth_number, hdmf_number),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        return self._row_to_employer(row)
