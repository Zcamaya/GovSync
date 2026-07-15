import os
import shutil

from services import auth_manager


class AuthController:
    def __init__(self, auth_service=None):
        self.auth_service = auth_service

    def login(self, username: str, password: str):
        return auth_manager.authenticate(username, password)

    def register(
        self,
        username: str,
        password: str,
        sss_number="",
        philhealth_number="",
        hdmf_number="",
        employer_name="",
        employer_id=None,
    ):
        return auth_manager.register_account(
            username,
            password,
            sss_number,
            philhealth_number,
            hdmf_number,
            employer_name=employer_name,
            employer_id=employer_id,
        )

    def list_accounts(self):
        return auth_manager.list_accounts()

    def delete_account(self, username: str):
        auth_manager.delete_account(username)
