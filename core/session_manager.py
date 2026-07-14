import json
import re
from pathlib import Path
from typing import Any

from config import DATA_DIR


def normalize_account_data(account: Any) -> dict[str, Any] | None:
    if not isinstance(account, dict):
        return None

    password_value = account.get("password_hash", account.get("password", ""))
    return {
        "username": str(account.get("username", "")).strip(),
        "password": str(password_value),
        "password_hash": str(password_value),
        "sss_number": SessionManager._digits_only(account.get("sss_number", "")),
        "philhealth_number": SessionManager._digits_only(account.get("philhealth_number", "")),
        "hdmf_number": SessionManager._digits_only(account.get("hdmf_number", "")),
        "employer_name": str(account.get("employer_name", "")).strip(),
    }


class SessionManager:
    _ACTIVE_ACCOUNT_FILENAME = "active_account.json"
    _ACCOUNT_FIELDS = (
        "username",
        "password",
        "password_hash",
        "sss_number",
        "philhealth_number",
        "hdmf_number",
        "employer_name",
    )

    def __init__(self, data_dir: Path | str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self._active_account: dict[str, Any] | None = None

    def app_data_dir(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir

    def active_account_path(self) -> Path:
        return self.app_data_dir() / self._ACTIVE_ACCOUNT_FILENAME

    @staticmethod
    def _digits_only(value: Any) -> str:
        return "".join(re.findall(r"\d", str(value)))

    def _normalize_account(self, account: Any) -> dict[str, Any] | None:
        return normalize_account_data(account)

    def set_active_account(self, account: Any | None) -> None:
        self._active_account = self._normalize_account(account) if account else None
        path = self.active_account_path()
        if self._active_account:
            with open(path, "w", encoding="utf-8") as output_file:
                json.dump(self._active_account, output_file, indent=2)
        elif path.exists():
            try:
                path.unlink()
            except OSError:
                pass

    def get_active_account(self) -> dict[str, Any] | None:
        if self._active_account is not None:
            return self._active_account

        path = self.active_account_path()
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
        except (OSError, json.JSONDecodeError):
            data = None

        if isinstance(data, dict):
            self._active_account = self._normalize_account(data)
            return self._active_account

        return None

    def clear_active_account(self) -> None:
        self.set_active_account(None)


_session_manager = SessionManager()


def get_active_account() -> dict[str, Any] | None:
    return _session_manager.get_active_account()


def set_active_account(account: Any | None) -> None:
    _session_manager.set_active_account(account)


def clear_active_account() -> None:
    _session_manager.clear_active_account()
