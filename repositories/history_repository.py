import json
from pathlib import Path

from models.history import HistoryRecord
from storage.sqlite import connect, initialize_database


class HistoryRepository:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def save(self, record: HistoryRecord) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO history_records (
                    id, account_username, module, period_label, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
                ON CONFLICT(id) DO UPDATE SET
                    account_username = excluded.account_username,
                    module = excluded.module,
                    period_label = excluded.period_label,
                    payload_json = excluded.payload_json,
                    created_at = COALESCE(excluded.created_at, history_records.created_at)
                """,
                (
                    record.id,
                    record.account_username,
                    record.module,
                    record.period_label,
                    record.payload_json,
                    record.created_at,
                ),
            )
            connection.commit()

    def list_by_account(self, account_username: str) -> list[HistoryRecord]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT * FROM history_records
                WHERE account_username = ?
                ORDER BY created_at DESC
                """,
                (account_username,),
            ).fetchall()
        records: list[HistoryRecord] = []
        for row in rows:
            records.append(
                HistoryRecord(
                    id=row["id"],
                    account_username=row["account_username"],
                    module=row["module"],
                    period_label=row["period_label"],
                    payload_json=row["payload_json"],
                    created_at=row["created_at"],
                    extra={"payload": self._parse_payload(row["payload_json"])},
                )
            )
        return records

    def delete_by_id(self, record_id: str) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                "DELETE FROM history_records WHERE id = ?",
                (record_id,),
            )
            connection.commit()

    def replace_many(self, account_username: str, records: list[HistoryRecord]) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                "DELETE FROM history_records WHERE account_username = ?",
                (account_username,),
            )
            for record in records:
                connection.execute(
                    """
                    INSERT INTO history_records (
                        id, account_username, module, period_label, payload_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.account_username,
                        record.module,
                        record.period_label,
                        record.payload_json,
                        record.created_at,
                    ),
                )
            connection.commit()

    @staticmethod
    def _parse_payload(payload_json: str):
        try:
            return json.loads(payload_json)
        except json.JSONDecodeError:
            return {}
