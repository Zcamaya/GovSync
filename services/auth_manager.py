import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from config import DATA_DIR, SUPER_ADMIN_PASSWORD, SUPER_ADMIN_USERNAME
from core.exceptions import AuthenticationError
from core.session_manager import clear_active_account, get_active_account, normalize_account_data, set_active_account
from models.account import Account
from models.employer import Employer
from repositories.account_repository import AccountRepository
from repositories.employer_repository import EmployerRepository
from services.auth_service import AuthService
from storage.sqlite import initialize_database

SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]")
ACCOUNT_NUMBER_LENGTHS = {
    "sss_number": 10,
    "philhealth_number": 12,
    "hdmf_number": 12,
}
_account_repository: AccountRepository | None = None
_auth_service: AuthService | None = None


def database_path() -> Path:
    from config import DATABASE_PATH

    return DATABASE_PATH


def _get_account_repository() -> AccountRepository:
    global _account_repository
    if _account_repository is None:
        initialize_database(database_path())
        _account_repository = AccountRepository(database_path())
    return _account_repository


def _get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService(_get_account_repository())
    return _auth_service


def _resolve_employer_id(employer_id: int | None, employer_name: str) -> int | None:
    if employer_id is not None:
        return int(employer_id)

    normalized_name = employer_name.strip()
    if not normalized_name:
        return None

    repository = EmployerRepository(database_path())
    existing = repository.get_by_name(normalized_name)
    if existing is not None:
        return existing.id

    created = repository.save(Employer(name=normalized_name, status="active"))
    return created.id


def account_folder_path(username: str) -> str:
    safe_name = SAFE_NAME_PATTERN.sub("_", username.strip() or "default")
    return os.path.join(app_data_dir(), "accounts", safe_name)


def account_folder(username: str) -> str:
    folder = account_folder_path(username)
    os.makedirs(folder, exist_ok=True)
    return folder


def app_data_dir() -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return str(DATA_DIR)


def account_json_path(username: str, filename: str) -> str:
    return os.path.join(account_folder(username), filename)


def normalize_account(account: Any) -> dict[str, str] | None:
    return normalize_account_data(account)


def digits_only(value: Any) -> str:
    return "".join(re.findall(r"\d", str(value)))


def validate_username(username: str) -> None:
    if not username.strip():
        raise ValueError("Username is required.")
    if username.lower() == SUPER_ADMIN_USERNAME:
        raise ValueError("That username is reserved.")


def validate_password(password: str) -> None:
    if not password:
        raise ValueError("Password is required.")


def validate_account_numbers(sss_number: str = "", philhealth_number: str = "", hdmf_number: str = "") -> None:
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
        if not raw_value:
            continue

        digits = digits_only(raw_value)
        expected_length = ACCOUNT_NUMBER_LENGTHS[field]
        if len(digits) != expected_length:
            raise ValueError(f"{labels[field]} must contain exactly {expected_length} digits.")


def _save_active_account(account: dict[str, str] | None) -> None:
    set_active_account(account)


def list_accounts() -> list[Account]:
    return _get_account_repository().list_all()


def load_accounts() -> list[dict[str, str]]:
    return [
        {
            "username": account.username,
            "password": account.password_hash,
            "password_hash": account.password_hash,
            "sss_number": account.sss_number,
            "philhealth_number": account.philhealth_number,
            "hdmf_number": account.hdmf_number,
            "employer_id": account.employer_id,
            "employer_name": account.employer_name,
        }
        for account in list_accounts()
    ]


def save_accounts(accounts: list[dict[str, Any]]) -> None:
    normalized_accounts: list[Account] = []
    for account in accounts:
        normalized = normalize_account(account)
        if normalized is None:
            continue
        normalized_accounts.append(
            Account(
                username=normalized["username"],
                password_hash=normalized["password"],
                sss_number=normalized["sss_number"],
                philhealth_number=normalized["philhealth_number"],
                hdmf_number=normalized["hdmf_number"],
                employer_id=normalized.get("employer_id"),
                employer_name=normalized["employer_name"],
            )
        )
    _get_account_repository().replace_all(normalized_accounts)


def get_account(username: str) -> dict[str, str] | None:
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
        "employer_id": account.employer_id,
        "employer_name": account.employer_name,
    }


def register_account(
    username: str,
    password: str,
    sss_number: str = "",
    philhealth_number: str = "",
    hdmf_number: str = "",
    employer_name: str = "",
    employer_id: int | None = None,
) -> Account:
    username = username.strip()
    password = password.strip()
    validate_username(username)
    validate_password(password)
    validate_account_numbers(sss_number, philhealth_number, hdmf_number)

    if get_account(username):
        raise ValueError("Username already exists.")

    employer_name = employer_name.strip()
    resolved_employer_id = _resolve_employer_id(employer_id, employer_name)
    account = Account(
        username=username,
        password_hash="",
        sss_number=digits_only(sss_number),
        philhealth_number=digits_only(philhealth_number),
        hdmf_number=digits_only(hdmf_number),
        employer_id=resolved_employer_id,
        employer_name=employer_name,
    )
    saved = _get_auth_service().register(account, password)
    account_folder(saved.username)
    return saved


def authenticate(username: str, password: str) -> str:
    username = username.strip()
    password = password.strip()

    if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
        account_folder(username)
        _save_active_account(
            {
                "username": username,
                "password": password,
                "password_hash": password,
                "sss_number": "",
                "philhealth_number": "",
                "hdmf_number": "",
                "employer_id": None,
                "employer_name": "",
            }
        )
        return "admin"

    try:
        account = _get_auth_service().authenticate(username, password)
    except AuthenticationError:
        clear_active_account()
        return ""

    account_folder(username)
    _save_active_account(
        {
            "username": account.username,
            "password": account.password_hash,
            "password_hash": account.password_hash,
            "sss_number": account.sss_number,
            "philhealth_number": account.philhealth_number,
            "hdmf_number": account.hdmf_number,
            "employer_id": account.employer_id,
            "employer_name": account.employer_name,
        }
    )
    return "user"


def delete_account(username: str) -> None:
    _get_account_repository().delete_by_username(username)
    folder = account_folder_path(username)
    if os.path.isdir(folder):
        shutil.rmtree(folder, ignore_errors=True)
    active = get_active_account() or {}
    if active.get("username", "").lower() == username.strip().lower():
        clear_active_account()


def update_account(username: str, **fields: Any) -> None:
    account = get_account(username)
    if not account:
        return

    merged = normalize_account(account)
    for key, value in fields.items():
        if key in ("username", "password", "password_hash", "sss_number", "philhealth_number", "hdmf_number", "employer_name"):
            if key in {"sss_number", "philhealth_number", "hdmf_number"}:
                merged[key] = digits_only(value)
            else:
                merged[key] = str(value).strip()

    _get_account_repository().save(
        Account(
            username=merged["username"],
            password_hash=merged["password"],
            sss_number=merged["sss_number"],
            philhealth_number=merged["philhealth_number"],
            hdmf_number=merged["hdmf_number"],
            employer_id=merged.get("employer_id"),
            employer_name=merged["employer_name"],
        )
    )
    active = get_active_account() or {}
    if active.get("username", "").lower() == username.strip().lower():
        _save_active_account(merged)
