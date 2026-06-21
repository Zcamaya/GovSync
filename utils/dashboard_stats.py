import calendar
import datetime
import json
import os
import re

from utils.account_store import global_json_path


STATS_FILENAME = "dashboard_stats.json"
MODULES = ("philhealth", "sss", "hdmf")
MONTH_NAMES = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}
_refresh_callback = None


def set_refresh_callback(callback):
    global _refresh_callback
    _refresh_callback = callback


def _notify():
    if _refresh_callback:
        _refresh_callback()


def stats_path():
    return global_json_path(STATS_FILENAME)


def load_stats():
    path = stats_path()
    if not os.path.exists(path):
        return {module: {} for module in MODULES}

    try:
        with open(path, "r", encoding="utf-8") as input_file:
            data = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return {module: {} for module in MODULES}

    if not isinstance(data, dict):
        return {module: {} for module in MODULES}

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
    return normalized


def save_stats(data):
    os.makedirs(os.path.dirname(stats_path()), exist_ok=True)
    with open(stats_path(), "w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=2)
    _notify()


def past_month_key(reference_date=None):
    reference = reference_date or datetime.date.today()
    first_of_month = reference.replace(day=1)
    previous_month = first_of_month - datetime.timedelta(days=1)
    return f"{previous_month.year}-{previous_month.month:02d}"


def period_key(month, year):
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


def record_upload(module, employee_count, month, year):
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


def get_past_month_total(module):
    module = str(module or "").strip().lower()
    key = past_month_key()
    stats = load_stats()
    total = stats.get(module, {}).get(key)
    if total is not None:
        return total

    if module == "philhealth":
        return _philhealth_total_from_history(key)

    return 0


def get_all_past_month_totals():
    return {
        "philhealth": get_past_month_total("philhealth"),
        "sss": get_past_month_total("sss"),
        "hdmf": get_past_month_total("hdmf"),
    }


def _philhealth_total_from_history(period_key):
    history_path = global_json_path("philhealth_history.json")
    if not os.path.exists(history_path):
        return 0

    try:
        with open(history_path, "r", encoding="utf-8") as input_file:
            records = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return 0

    if not isinstance(records, list):
        return 0

    for record in reversed(records):
        if not isinstance(record, dict):
            continue
        if period_key_from_label(record.get("month_year", "")) == period_key:
            try:
                return int(record.get("total_count", 0))
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
