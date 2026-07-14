import json

from models.history import HistoryRecord
from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from services.dashboard_service import period_key_from_label
import services.philhealth_engine as philhealth_engine


class PhilHealthService:
    def __init__(
        self,
        history_repository: HistoryRepository,
        statistics_repository: StatisticsRepository,
        message_box_class=None,
    ):
        self.history_repository = history_repository
        self.statistics_repository = statistics_repository
        self.message_box_class = message_box_class

    def _apply_message_box_override(self):
        if self.message_box_class is not None:
            philhealth_engine.QMessageBox = self.message_box_class

    def create_engine(self):
        self._apply_message_box_override()
        return philhealth_engine.PhicExtractorApp()

    def process(self, engine=None, progress_callback=None):
        if engine is None:
            engine = self.create_engine()
        return engine.process_files(progress_callback=progress_callback)

    def list_history(self, account_username: str) -> list[dict]:
        records = self.history_repository.list_by_account(account_username)
        return [
            record.extra.get("payload", {})
            for record in records
            if isinstance(record.extra.get("payload", {}), dict)
        ]

    def save_history(self, account_username: str, record_data: dict) -> None:
        record = dict(record_data)
        self.history_repository.save(
            HistoryRecord(
                id=str(record.get("id", "")),
                account_username=account_username,
                module="philhealth",
                period_label=str(record.get("month_year", "")),
                payload_json=json.dumps(record),
                created_at=record.get("created_at"),
                extra={"payload": record},
            )
        )
        period_key = period_key_from_label(record.get("month_year", ""))
        self.statistics_repository.upsert_total(
            account_username,
            "philhealth",
            period_key or str(record.get("month_year", "")),
            int(record.get("total_count", 0)),
        )

    def delete_history(self, account_username, record_id):
        records = self.history_repository.list_by_account(account_username)
        matching_record = next((record for record in records if record.id == record_id), None)
        if matching_record is None:
            return
        self.history_repository.delete_by_id(record_id, account_username)
