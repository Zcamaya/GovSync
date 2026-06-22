import json
import os
import re
import shutil

from core.exceptions import AuthenticationError
from config import DATA_DIR, SUPER_ADMIN_PASSWORD, SUPER_ADMIN_USERNAME
from models.account import Account
from repositories.account_repository import AccountRepository
from services.auth_service import AuthService
from storage.sqlite import initialize_database


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
_account_repository = None
_auth_service = None
_ACTIVE_ACCOUNT_FILENAME = "active_account.json"


def app_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return str(DATA_DIR)


def database_path():
    from config import DATABASE_PATH

    return DATABASE_PATH


def active_account_path():
    return os.path.join(app_data_dir(), _ACTIVE_ACCOUNT_FILENAME)


def account_folder(username):
    safe_name = SAFE_NAME_PATTERN.sub("_", username.strip() or "default")
    folder = os.path.join(app_data_dir(), "accounts", safe_name)
    os.makedirs(folder, exist_ok=True)
    return folder


def account_json_path(username, filename):
    return os.path.join(account_folder(username), filename)


def _get_account_repository():
    global _account_repository
    if _account_repository is None:
        initialize_database(database_path())
        _account_repository = AccountRepository(database_path())
    return _account_repository


def _get_auth_service():
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService(_get_account_repository())
    return _auth_service


def load_accounts():
    repository = _get_account_repository()
    return [
        {
            "username": account.username,
            "password": account.password_hash,
            "password_hash": account.password_hash,
            "sss_number": account.sss_number,
            "philhealth_number": account.philhealth_number,
            "hdmf_number": account.hdmf_number,
        }
        for account in repository.list_all()
    ]


def save_accounts(accounts):
    repository = _get_account_repository()
    normalized_accounts = []
    for account in accounts:
        normalized = normalize_account(account)
        normalized_accounts.append(
            Account(
                username=normalized["username"],
                password_hash=normalized["password"],
                sss_number=normalized["sss_number"],
                philhealth_number=normalized["philhealth_number"],
                hdmf_number=normalized["hdmf_number"],
            )
        )
    repository.replace_all(normalized_accounts)


def normalize_account(account):
    account = account if isinstance(account, dict) else {}
    password_value = account.get("password_hash", account.get("password", ""))
    return {
        "username": str(account.get("username", "")).strip(),
        "password": str(password_value),
        "sss_number": digits_only(account.get("sss_number", "")),
        "philhealth_number": digits_only(account.get("philhealth_number", "")),
        "hdmf_number": digits_only(account.get("hdmf_number", "")),
    }


def get_account(username):
    username = str(username or "").strip()
    if not username:
        return None

    account = _get_account_repository().get_by_username(username)
    if account is None:
        return None

    return {
        "username": account.username,
        "password": account.password_hash,
        "password_hash": account.password_hash,
        "sss_number": account.sss_number,
        "philhealth_number": account.philhealth_number,
        "hdmf_number": account.hdmf_number,
    }


def set_active_account(account):
    global _active_account
    _active_account = normalize_account(account) if account else None
    path = active_account_path()
    if _active_account:
        with open(path, "w", encoding="utf-8") as output_file:
            json.dump(_active_account, output_file, indent=2)
    elif os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


def get_active_account():
    global _active_account
    if _active_account:
        return normalize_account(_active_account)

    path = active_account_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as input_file:
                data = json.load(input_file)
        except (OSError, json.JSONDecodeError):
            data = None
        if isinstance(data, dict):
            _active_account = normalize_account(data)
            return normalize_account(_active_account)

    return None


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

    if get_account(username):
        raise ValueError("Username already exists.")

    try:
        _get_auth_service().register(
            Account(
                username=username,
                password_hash="",
                sss_number=digits_only(sss_number),
                philhealth_number=digits_only(philhealth_number),
                hdmf_number=digits_only(hdmf_number),
            ),
            password,
        )
    except AuthenticationError as exc:
        raise ValueError(str(exc)) from exc

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

    try:
        account = _get_auth_service().authenticate(username, password)
    except AuthenticationError:
        set_active_account(None)
        return ""

    account_folder(username)
    set_active_account(
        {
            "username": account.username,
            "password": account.password_hash,
            "sss_number": account.sss_number,
            "philhealth_number": account.philhealth_number,
            "hdmf_number": account.hdmf_number,
        }
    )
    return "user"


def delete_account(username):
    _get_account_repository().delete_by_username(username)
    folder = account_folder(username)
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)
    active = get_active_account() or {}
    if active.get("username", "").lower() == str(username).strip().lower():
        set_active_account(None)


def update_account(username, **fields):
    account = get_account(username)
    if not account:
        return

    merged = normalize_account(account)
    for key, value in fields.items():
        if key in ACCOUNT_FIELDS:
            merged[key] = str(value).strip()

    _get_account_repository().save(
        Account(
            username=merged["username"],
            password_hash=merged["password"],
            sss_number=merged["sss_number"],
            philhealth_number=merged["philhealth_number"],
            hdmf_number=merged["hdmf_number"],
        )
    )
    if _active_account and _active_account.get("username", "").lower() == str(username).strip().lower():
        set_active_account(merged)
