import json
import os
import re
import shutil

from PySide6.QtCore import QStandardPaths


SUPER_ADMIN_USERNAME = "superadmin"
SUPER_ADMIN_PASSWORD = "admin1234"
SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")
ACCOUNT_FIELDS = (
    "username",
    "password",
    "sss_number",
    "philhealth_number",
    "hdmf_number",
)
ACCOUNT_NUMBER_LENGTHS = {
    "sss_number": 10,
    "philhealth_number": 12,
    "hdmf_number": 12,
}
_active_account = None


def accounts_path():
    base_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    if not base_dir:
        base_dir = os.path.join(os.path.expanduser("~"), ".govsync")
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "accounts.json")


def app_data_dir():
    return os.path.dirname(accounts_path())


def global_json_path(filename):
    return os.path.join(app_data_dir(), filename)


def account_folder(username):
    safe_name = SAFE_NAME_PATTERN.sub("_", username.strip() or "default")
    folder = os.path.join(app_data_dir(), "accounts", safe_name)
    os.makedirs(folder, exist_ok=True)
    return folder


def account_json_path(username, filename):
    return os.path.join(account_folder(username), filename)


def load_accounts():
    path = accounts_path()
    if not os.path.exists(path):
        save_accounts([])
        return []

    try:
        with open(path, "r", encoding="utf-8") as input_file:
            data = json.load(input_file)
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [normalize_account(account) for account in data]


def save_accounts(accounts):
    normalized = [normalize_account(account) for account in accounts]
    with open(accounts_path(), "w", encoding="utf-8") as output_file:
        json.dump(normalized, output_file, indent=2)


def normalize_account(account):
    account = account if isinstance(account, dict) else {}
    return {
        "username": str(account.get("username", "")).strip(),
        "password": str(account.get("password", "")),
        "sss_number": digits_only(account.get("sss_number", "")),
        "philhealth_number": digits_only(account.get("philhealth_number", "")),
        "hdmf_number": digits_only(account.get("hdmf_number", "")),
    }


def get_account(username):
    username = str(username or "").strip()
    if not username:
        return None

    for account in load_accounts():
        if account.get("username", "").lower() == username.lower():
            return normalize_account(account)
    return None


def set_active_account(account):
    global _active_account
    _active_account = normalize_account(account) if account else None


def get_active_account():
    return normalize_account(_active_account) if _active_account else None


def validate_username(username):
    if not username.strip():
        raise ValueError("Username is required.")
    if username.lower() == SUPER_ADMIN_USERNAME:
        raise ValueError("That username is reserved.")


def validate_password(password):
    if not password:
        raise ValueError("Password is required.")


def digits_only(value):
    return "".join(re.findall(r"\d", str(value)))


def validate_account_numbers(sss_number="", philhealth_number="", hdmf_number=""):
    values = {
        "sss_number": sss_number,
        "philhealth_number": philhealth_number,
        "hdmf_number": hdmf_number,
    }
    labels = {
        "sss_number": "SSS Number",
        "philhealth_number": "PhilHealth Number",
        "hdmf_number": "HDMF Number",
    }

    for field, raw_value in values.items():
        digits = digits_only(raw_value)
        expected_length = ACCOUNT_NUMBER_LENGTHS[field]
        if len(digits) != expected_length:
            raise ValueError(f"{labels[field]} must contain exactly {expected_length} digits.")


def register_account(
    username,
    password,
    sss_number="",
    philhealth_number="",
    hdmf_number="",
):
    username = username.strip()
    password = password.strip()
    validate_username(username)
    validate_password(password)
    validate_account_numbers(sss_number, philhealth_number, hdmf_number)

    accounts = load_accounts()
    if any(account["username"].lower() == username.lower() for account in accounts):
        raise ValueError("Username already exists.")

    accounts.append(
        normalize_account(
            {
                "username": username,
                "password": password,
                "sss_number": digits_only(sss_number),
                "philhealth_number": digits_only(philhealth_number),
                "hdmf_number": digits_only(hdmf_number),
            }
        )
    )
    save_accounts(accounts)
    account_folder(username)


def authenticate(username, password):
    username = username.strip()
    password = password.strip()

    if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
        account_folder(username)
        set_active_account(
            {
                "username": username,
                "password": password,
                "sss_number": "",
                "philhealth_number": "",
                "hdmf_number": "",
            }
        )
        return "admin"

    for account in load_accounts():
        if account.get("username") == username and account.get("password") == password:
            account_folder(username)
            set_active_account(account)
            return "user"

    set_active_account(None)
    return ""


def delete_account(username):
    accounts = [
        account for account in load_accounts() if account.get("username") != username
    ]
    save_accounts(accounts)
    folder = account_folder(username)
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)


def update_account(username, **fields):
    accounts = load_accounts()
    updated = False
    for index, account in enumerate(accounts):
        if account.get("username", "").lower() == str(username).strip().lower():
            merged = normalize_account(account)
            merged.update({key: str(value).strip() for key, value in fields.items() if key in ACCOUNT_FIELDS})
            accounts[index] = normalize_account(merged)
            updated = True
            break

    if updated:
        save_accounts(accounts)
        if _active_account and _active_account.get("username", "").lower() == str(username).strip().lower():
            set_active_account(accounts[index])
