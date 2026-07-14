import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import config
import storage.sqlite as sqlite_storage
from PySide6.QtWidgets import QApplication
from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from services.philhealth_service import PhilHealthService
from widgets.philhealth_panel import PhilHealthPanel


class PhilHealthAccountScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_philhealth.sqlite"
        config.DATABASE_PATH = self.db_path
        sqlite_storage.DATABASE_PATH = self.db_path

    def tearDown(self) -> None:
        import gc

        gc.collect()
        self.temp_dir.cleanup()

    def test_reset_process_view_clears_stale_metrics_when_no_history_exists(self) -> None:
        app = QApplication.instance() or QApplication([])
        panel = PhilHealthPanel(controller=None)
        panel.engine.history_records = []
        panel._restore_latest_process_state()

        self.assertEqual(panel.engine.card_month.value_lbl.text(), "Pending")
        self.assertEqual(panel.engine.card_total.value_lbl.text(), "0")
        self.assertEqual(panel.engine.card_missing.value_lbl.text(), "0")
        self.assertEqual(panel.engine.card_new.value_lbl.text(), "0")
        self.assertEqual(panel.progress_note_label.text(), "No history for this account yet.")
        self.assertEqual(panel.progress_percent_label.text(), "0%")
        app.processEvents()
        panel.deleteLater()

    def test_history_is_scoped_to_account_and_delete_respects_account(self) -> None:
        history_repository = HistoryRepository(self.db_path)
        statistics_repository = StatisticsRepository(self.db_path)
        service = PhilHealthService(history_repository, statistics_repository)

        first_record = {
            "id": "record-a",
            "month_year": "January 2024",
            "total_count": 5,
            "missing_count": 1,
            "new_count": 0,
            "data_total": [["Client A", "123456789012", "Name A", "1990-01-01"]],
            "data_missing": [["Client A", "123456789012", "Name A", "1990-01-01"]],
            "data_new": [],
        }
        second_record = {
            "id": "record-b",
            "month_year": "February 2024",
            "total_count": 6,
            "missing_count": 0,
            "new_count": 1,
            "data_total": [["Client B", "987654321098", "Name B", "1991-01-01"]],
            "data_missing": [],
            "data_new": [["Client B", "987654321098", "Name B", "1991-01-01"]],
        }

        service.save_history("acct-a", first_record)
        service.save_history("acct-b", second_record)

        first_history = service.list_history("acct-a")
        second_history = service.list_history("acct-b")

        self.assertEqual(len(first_history), 1)
        self.assertEqual(first_history[0]["month_year"], "January 2024")
        self.assertEqual(len(second_history), 1)
        self.assertEqual(second_history[0]["month_year"], "February 2024")

        service.delete_history("acct-a", "record-a")

        self.assertEqual(service.list_history("acct-a"), [])
        self.assertEqual(service.list_history("acct-b")[0]["month_year"], "February 2024")


if __name__ == "__main__":
    unittest.main()
