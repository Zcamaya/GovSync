from typing import Any

from services.auth_manager import account_json_path


def resolve_account_username(account_or_username: Any, default: str = "default") -> str:
    if isinstance(account_or_username, dict):
        value = account_or_username.get("username", "")
    else:
        value = account_or_username
    return str(value or "").strip() or default


def account_state_path(account_or_username: Any, filename: str, default: str = "default") -> str:
    return account_json_path(resolve_account_username(account_or_username, default), filename)
