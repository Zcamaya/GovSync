from pathlib import Path

from storage.sqlite import connect, initialize_database


class StatisticsRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def upsert_total(self, account_username: str, module: str, period_key: str, total_count: int) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO statistics (account_username, module, period_key, total_count)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(account_username, module, period_key) DO UPDATE SET
                    total_count = excluded.total_count
                """,
                (account_username, module, period_key, total_count),
            )
            connection.commit()

    def get_total(self, account_username: str, module: str, period_key: str) -> int:
        with connect(self.database_path) as connection:
            row = connection.execute(
                """
                SELECT total_count FROM statistics
                WHERE account_username = ? AND module = ? AND period_key = ?
                """,
                (account_username, module, period_key),
            ).fetchone()
        return int(row["total_count"]) if row else 0

    def list_by_account(self, account_username: str) -> dict[str, dict[str, int]]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT module, period_key, total_count
                FROM statistics
                WHERE account_username = ?
                """,
                (account_username,),
            ).fetchall()

        data: dict[str, dict[str, int]] = {}
        for row in rows:
            module = row["module"]
            data.setdefault(module, {})[row["period_key"]] = int(row["total_count"])
        return data

    def replace_many(self, account_username: str, data: dict[str, dict[str, int]]) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                "DELETE FROM statistics WHERE account_username = ?",
                (account_username,),
            )
            for module, periods in data.items():
                for period_key, total_count in periods.items():
                    connection.execute(
                        """
                        INSERT INTO statistics (account_username, module, period_key, total_count)
                        VALUES (?, ?, ?, ?)
                        """,
                        (account_username, module, str(period_key), int(total_count)),
                    )
            connection.commit()
