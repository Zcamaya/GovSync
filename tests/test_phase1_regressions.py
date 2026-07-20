import os
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import config
import services.auth_manager as auth_manager
import services.payroll_import_service as payroll_import_service
import storage.sqlite as sqlite_storage
from PySide6.QtWidgets import QApplication
from widgets.sss_panel import SSSPanel


def _reset_auth_manager_state() -> None:
    auth_manager._account_repository = None
    auth_manager._auth_service = None


@pytest.fixture()
def temp_database(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "govsync_test.sqlite"
        monkeypatch.setattr(config, "DATABASE_PATH", db_path, raising=False)
        monkeypatch.setattr(sqlite_storage, "DATABASE_PATH", db_path, raising=False)
        _reset_auth_manager_state()
        yield db_path
        _reset_auth_manager_state()


def test_update_account_keeps_existing_password_hash_when_profile_fields_change(
    temp_database,
    monkeypatch,
):
    monkeypatch.setattr(auth_manager, "account_folder", lambda username: None)

    created = auth_manager.register_account(
        username="profile-user",
        password="secret123",
        employer_name="Acme Corp",
    )
    original = auth_manager.get_account(created.username)

    auth_manager.update_account(created.username, employer_name="Beta Corp")

    updated = auth_manager.get_account(created.username)
    assert updated is not None
    assert updated["password_hash"] == original["password_hash"]
    assert updated["employer_name"] == "Beta Corp"


def test_update_account_rehashes_password_when_password_changes(temp_database, monkeypatch):
    monkeypatch.setattr(auth_manager, "account_folder", lambda username: None)

    created = auth_manager.register_account(
        username="password-user",
        password="secret123",
        employer_name="Acme Corp",
    )

    auth_manager.update_account(created.username, password="newsecret")

    updated = auth_manager.get_account(created.username)
    assert updated is not None
    assert updated["password_hash"] != "newsecret"
    assert updated["password_hash"].startswith(("bcrypt$", "pbkdf2$"))


class _FakePayrollRepository:
    def __init__(self):
        self.calls = []

    def initialize_schema(self):
        return None

    def file_hash(self, file_path):
        return "file-hash"

    def get_import_by_hash(self, file_hash):
        self.calls.append(("get_import_by_hash", file_hash))
        return None

    def get_payroll_import(self, employer_id, applicable_month, from_date, to_date, client_id):
        self.calls.append(
            (
                "get_payroll_import",
                employer_id,
                applicable_month,
                from_date,
                to_date,
                client_id,
            )
        )
        return None

    def get_payroll_import_for_month(self, employer_id, applicable_month, client_id):
        self.calls.append(
            (
                "get_payroll_import_for_month",
                employer_id,
                applicable_month,
                client_id,
            )
        )
        return None


def _sample_payroll_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "batchid": "B001",
                "fdate": "2026-06-01",
                "tdate": "2026-06-15",
                "custid": "C001",
                "company": "Client Alpha",
                "emplid": "E001",
                "lastname": "Doe",
                "firstname": "Jane",
                "middlename": "Q",
                "suffix": "",
                "birthdate": "1990-01-01",
                "basicrate": "1000",
                "billrate": "1200",
                "sssno": "1234567890",
                "sss": "100",
                "eeshare": "50",
                "ershare": "50",
                "sssrem": "0",
                "er": "0",
                "pagibigno": "123456789012",
                "pagibig": "100",
                "pagibigrem": "0",
                "phealthno": "123456789012",
                "phealth": "100",
                "phealthrem": "0",
                "sssloan": "0",
                "pbigloan": "0",
                "ctr": "0",
                "tinno": "123456789",
                "datehired": "2024-01-01",
                "companyid": "COMP-1",
                "position": "Clerk",
            }
        ]
    )


def test_build_import_plan_uses_active_account_employer_id(temp_database, monkeypatch):
    fake_repo = _FakePayrollRepository()
    service = payroll_import_service.PayrollImportService(repository=fake_repo)

    monkeypatch.setattr(
        payroll_import_service,
        "get_active_account",
        lambda: {
            "username": "acct-user",
            "employer_id": 77,
            "employer_name": "Acme Corp",
        },
    )
    monkeypatch.setattr(service, "inspect_workbook", lambda file_path: (_sample_payroll_frame(), "Earnings"))

    plan = service.build_import_plan("sample.xlsx", applicable_month="June 2026")

    assert plan.employer_id == "77"


def test_duplicate_lookup_uses_same_owner_identifier_as_saved_plan(temp_database, monkeypatch):
    fake_repo = _FakePayrollRepository()
    service = payroll_import_service.PayrollImportService(repository=fake_repo)

    monkeypatch.setattr(
        payroll_import_service,
        "get_active_account",
        lambda: {
            "username": "acct-user",
            "employer_id": 77,
            "employer_name": "Acme Corp",
        },
    )
    monkeypatch.setattr(service, "inspect_workbook", lambda file_path: (_sample_payroll_frame(), "Earnings"))

    plan = service.build_import_plan("sample.xlsx", applicable_month="June 2026")

    exact_lookup = next(call for call in fake_repo.calls if call[0] == "get_payroll_import")
    month_lookup = next(call for call in fake_repo.calls if call[0] == "get_payroll_import_for_month")

    assert exact_lookup[1] == plan.employer_id
    assert month_lookup[1] == plan.employer_id


class _DummySSSController:
    def generate_txt(self, *args, **kwargs):
        return "", 0

    def load_txt(self, file_path):
        return []

    def save_txt(self, rows, file_path):
        return file_path, len(rows)


def test_sss_banner_shows_when_account_has_linked_sss_number(monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance() or QApplication([])

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        monkeypatch.setattr(
            "widgets.sss_panel.account_json_path",
            lambda username, filename: str(temp_root / f"{username}_{filename}"),
        )
        monkeypatch.setattr("widgets.sss_panel.get_active_account", lambda: {})

        panel = SSSPanel(controller=_DummySSSController(), dashboard_service=None)
        panel.show()
        panel.set_account({"username": "acct-user", "sss_number": "1234567890"})
        app.processEvents()

        assert panel.account_banner.isVisible()
