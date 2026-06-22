from core.exceptions import AuthenticationError
from models.account import Account
from services.auth_service import AuthService
from utils.account_store import (
    account_folder,
    digits_only,
    get_active_account,
    SUPER_ADMIN_PASSWORD,
    SUPER_ADMIN_USERNAME,
    set_active_account,
    validate_account_numbers,
    validate_password,
    validate_username,
)
import os
import shutil


class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    def login(self, username: str, password: str):
        if username.strip() == SUPER_ADMIN_USERNAME and password.strip() == SUPER_ADMIN_PASSWORD:
            set_active_account(
                {
                    "username": SUPER_ADMIN_USERNAME,
                    "password": SUPER_ADMIN_PASSWORD,
                    "sss_number": "",
                    "philhealth_number": "",
                    "hdmf_number": "",
                }
            )
            return "admin"

        try:
            account = self.auth_service.authenticate(username, password)
        except AuthenticationError:
            set_active_account(None)
            return ""

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

    def register(self, username: str, password: str, sss_number="", philhealth_number="", hdmf_number=""):
        validate_username(username.strip())
        validate_password(password.strip())
        validate_account_numbers(sss_number, philhealth_number, hdmf_number)
        account = Account(
            username=username.strip(),
            password_hash="",
            sss_number=digits_only(sss_number),
            philhealth_number=digits_only(philhealth_number),
            hdmf_number=digits_only(hdmf_number),
        )
        saved = self.auth_service.register(account, password)
        account_folder(saved.username)
        return saved

    def list_accounts(self):
        return self.auth_service.account_repository.list_all()

    def delete_account(self, username: str):
        self.auth_service.account_repository.delete_by_username(username)
        folder = account_folder(username)
        if os.path.isdir(folder):
            shutil.rmtree(folder, ignore_errors=True)
        active = get_active_account() or {}
        if active.get("username", "").lower() == str(username).strip().lower():
            set_active_account(None)
