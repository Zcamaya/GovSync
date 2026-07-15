import calendar
import datetime
import re
from typing import Any

from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from services.auth_manager import database_path, get_active_account
from services.history_service import HistoryService
from services.statistics_service import StatisticsService
from storage.sqlite import initialize_database

MODULES = ("philhealth", "sss", "hdmf")
MONTH_NAMES = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}


class DashboardService:
    def __init__(self, statistics_service: StatisticsService, history_service: HistoryService):
        self.statistics_service = statistics_service
        self.history_service = history_service
        self._refresh_callbacks: list[Any] = []

    def _account_username(self, default: str = "default") -> str:
        active_account = get_active_account() or {}
        return active_account.get("username") or default

    def register_refresh_callback(self, callback) -> None:
        if callable(callback) and callback not in self._refresh_callbacks:
            self._refresh_callbacks.append(callback)

    def _notify_refresh(self) -> None:
        for callback in list(self._refresh_callbacks):
            try:
                callback()
            except Exception:
                pass

    def _normalize_stats(self, data: dict[str, dict[str, int]]) -> dict[str, dict[str, int]]:
        normalized: dict[str, dict[str, int]] = {module: {} for module in MODULES}
        for module, module_data in data.items():
            if module not in MODULES or not isinstance(module_data, dict):
                continue
            for key, value in module_data.items():
                try:
                    normalized[module][str(key)] = int(value)
                except (TypeError, ValueError):
                    continue
        return normalized

    def list_totals_for_account(self, account_username: str | None = None) -> dict[str, dict[str, int]]:
        account_username = account_username or self._account_username()
        return self.statistics_service.list_totals_for_account(account_username)

    def replace_totals_for_account(self, account_username: str, data: dict[str, dict[str, int]]) -> None:
        normalized = self._normalize_stats(data)
        self.statistics_service.replace_totals_for_account(account_username, normalized)
        self._notify_refresh()

    def get_past_month_total(self, module: str, account_username: str | None = None) -> int:
        module = str(module or "").strip().lower()
        username = account_username or self._account_username()
        key = self.past_month_key()
        totals = self.list_totals_for_account(username)
        total = totals.get(module, {}).get(key)
        if total is not None:
            return total

        if module == "philhealth":
            return self._philhealth_total_from_history(key, username)

        return 0

    def get_all_past_month_totals(self, account_username: str | None = None) -> dict[str, int]:
        return {module: self.get_past_month_total(module, account_username=account_username) for module in MODULES}

    def record_upload(self, module: str, employee_count, month, year, account_username: str | None = None) -> None:
        module = str(module or "").strip().lower()
        if module not in MODULES:
            return

        try:
            count = int(employee_count)
        except (TypeError, ValueError):
            return

        username = account_username or self._account_username()
        key = self.period_key(month, year)
        stats = self.list_totals_for_account(username)
        stats.setdefault(module, {})[key] = count
        self.replace_totals_for_account(username, stats)

    def period_key(self, month, year) -> str:
        month_index = self._month_to_index(month)
        year_value = self._year_to_int(year)
        if month_index is None or year_value is None:
            return self.past_month_key()
        return f"{year_value}-{month_index:02d}"

    def period_key_from_label(self, label):
        text = str(label or "").strip()
        if not text:
            return None

        match = re.match(r"^([A-Za-z]+)\s+(\d{4})$", text)
        if not match:
            return None

        return self.period_key(match.group(1), match.group(2))

    def past_month_key(self, reference_date=None) -> str:
        reference = reference_date or datetime.date.today()
        first_of_month = reference.replace(day=1)
        previous_month = first_of_month - datetime.timedelta(days=1)
        return f"{previous_month.year}-{previous_month.month:02d}"

    def _philhealth_total_from_history(self, period_key, account_username: str | None = None) -> int:
        username = account_username or self._account_username()
        records = self.history_service.list_for_account(username)
        for record in reversed(records):
            payload = record.extra.get("payload", {}) if record.extra else {}
            if self.period_key_from_label(payload.get("month_year", "")) == period_key:
                try:
                    return int(payload.get("total_count", 0))
                except (TypeError, ValueError):
                    return 0
        return 0

    def _month_to_index(self, month):
        if month is None:
            return None

        if isinstance(month, int):
            return month if 1 <= month <= 12 else None

        text = str(month).strip()
        if not text:
            return None

        if text.isdigit():
            value = int(text)
            return value if 1 <= value <= 12 else None

        normalized = text.lower()
        if normalized in MONTH_NAMES:
            return MONTH_NAMES[normalized]

        for name, index in MONTH_NAMES.items():
            if name.startswith(normalized[:3]):
                return index
        return None

    def _year_to_int(self, year):
        if year is None:
            return None

        text = str(year).strip()
        if not text.isdigit():
            return None

        return int(text)


def _build_default_dashboard_service() -> DashboardService:
    initialize_database(database_path())
    statistics_service = StatisticsService(StatisticsRepository(database_path()))
    history_service = HistoryService(HistoryRepository(database_path()))
    return DashboardService(statistics_service, history_service)


_default_dashboard_service = _build_default_dashboard_service()


def get_account_username(default: str = "default") -> str:
    return _default_dashboard_service._account_username(default)


def period_key_from_label(label):
    return _default_dashboard_service.period_key_from_label(label)


def record_upload(module, employee_count, month, year, account_username: str | None = None) -> None:
    return _default_dashboard_service.record_upload(module, employee_count, month, year, account_username)


def get_all_past_month_totals(account_username: str | None = None) -> dict[str, int]:
    return _default_dashboard_service.get_all_past_month_totals(account_username)


def set_refresh_callback(callback):
    _default_dashboard_service.register_refresh_callback(callback)
