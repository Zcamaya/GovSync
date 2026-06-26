import calendar
import datetime
import re

from repositories.history_repository import HistoryRepository
from repositories.statistics_repository import StatisticsRepository
from storage.sqlite import initialize_database
from services.auth_manager import database_path, get_active_account

MODULES = ("philhealth", "sss", "hdmf")
MONTH_NAMES = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}
_refresh_callback = None


def set_refresh_callback(callback):
    global _refresh_callback
    _refresh_callback = callback


def _notify():
    if _refresh_callback:
        _refresh_callback()


def _account_username():
    active_account = get_active_account() or {}
    return active_account.get("username") or "default"


def _stats_repository():
    initialize_database(database_path())
    return StatisticsRepository(database_path())


def _history_repository():
    initialize_database(database_path())
    return HistoryRepository(database_path())


def load_stats() -> dict[str, dict[str, int]]:
    repository = _stats_repository()
    username = _account_username()
    data = repository.list_by_account(username)
    return {module: data.get(module, {}) for module in MODULES}


def save_stats(data: dict[str, dict[str, int]]) -> None:
    repository = _stats_repository()
    username = _account_username()
    normalized = {module: {} for module in MODULES}
    for module in MODULES:
        module_data = data.get(module, {})
        if not isinstance(module_data, dict):
            continue
        for key, value in module_data.items():
            try:
                normalized[module][str(key)] = int(value)
            except (TypeError, ValueError):
                continue
    repository.replace_many(username, normalized)
    _notify()


def past_month_key(reference_date=None) -> str:
    reference = reference_date or datetime.date.today()
    first_of_month = reference.replace(day=1)
    previous_month = first_of_month - datetime.timedelta(days=1)
    return f"{previous_month.year}-{previous_month.month:02d}"


def period_key(month, year) -> str:
    month_index = _month_to_index(month)
    year_value = _year_to_int(year)
    if month_index is None or year_value is None:
        return past_month_key()
    return f"{year_value}-{month_index:02d}"


def period_key_from_label(label):
    text = str(label or "").strip()
    if not text:
        return None

    match = re.match(r"^([A-Za-z]+)\s+(\d{4})$", text)
    if not match:
        return None

    return period_key(match.group(1), match.group(2))


def record_upload(module, employee_count, month, year) -> None:
    module = str(module or "").strip().lower()
    if module not in MODULES:
        return

    try:
        count = int(employee_count)
    except (TypeError, ValueError):
        return

    key = period_key(month, year)
    stats = load_stats()
    stats[module][key] = count
    save_stats(stats)


def get_past_month_total(module) -> int:
    module = str(module or "").strip().lower()
    key = past_month_key()
    stats = load_stats()
    total = stats.get(module, {}).get(key)
    if total is not None:
        return total

    if module == "philhealth":
        return _philhealth_total_from_history(key)

    return 0


def get_all_past_month_totals() -> dict[str, int]:
    return {
        "philhealth": get_past_month_total("philhealth"),
        "sss": get_past_month_total("sss"),
        "hdmf": get_past_month_total("hdmf"),
    }


def _philhealth_total_from_history(period_key):
    repository = _history_repository()
    records = repository.list_by_account(_account_username())
    for record in reversed(records):
        payload = record.extra.get("payload", {}) if record.extra else {}
        if period_key_from_label(payload.get("month_year", "")) == period_key:
            try:
                return int(payload.get("total_count", 0))
            except (TypeError, ValueError):
                return 0
    return 0


def _month_to_index(month):
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


def _year_to_int(year):
    if year is None:
        return None

    text = str(year).strip()
    if not text.isdigit():
        return None

    return int(text)
