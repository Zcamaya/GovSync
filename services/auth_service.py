import base64
import binascii
import hashlib
import hmac
import os

from core.exceptions import AuthenticationError
from models.account import Account
from repositories.account_repository import AccountRepository

try:
    import bcrypt
except ImportError:  # pragma: no cover - scaffold fallback
    bcrypt = None


PBKDF2_ITERATIONS = 200_000


class AuthService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def register(self, account: Account, plain_password: str) -> Account:
        account.password_hash = self._hash_password(plain_password)
        return self.account_repository.save(account)

    def authenticate(self, username: str, plain_password: str) -> Account:
        account = self.account_repository.get_by_username(username)
        if account is None:
            raise AuthenticationError("Invalid username or password.")
        if not self._verify_password(account.password_hash, plain_password):
            raise AuthenticationError("Invalid username or password.")
        return account

    def _hash_password(self, plain_password: str) -> str:
        password_bytes = plain_password.encode("utf-8")
        if bcrypt is not None:
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            return "bcrypt$" + hashed.decode("utf-8")

        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password_bytes,
            salt,
            PBKDF2_ITERATIONS,
        )
        return "pbkdf2$%d$%s$%s" % (
            PBKDF2_ITERATIONS,
            base64.b64encode(salt).decode("ascii"),
            base64.b64encode(digest).decode("ascii"),
        )

    def _verify_password(self, stored_password: str, plain_password: str) -> bool:
        if not stored_password:
            return False

        password_bytes = plain_password.encode("utf-8")
        stored_value = str(stored_password)

        if stored_value.startswith("bcrypt$") and bcrypt is not None:
            encoded = stored_value.split("$", 1)[1].encode("utf-8")
            return bcrypt.checkpw(password_bytes, encoded)

        if stored_value.startswith("$2") and bcrypt is not None:
            return bcrypt.checkpw(password_bytes, stored_value.encode("utf-8"))

        if stored_value.startswith("pbkdf2$"):
            try:
                _, rounds_text, salt_text, digest_text = stored_value.split("$", 3)
                rounds = int(rounds_text)
                salt = base64.b64decode(salt_text.encode("ascii"))
                expected = base64.b64decode(digest_text.encode("ascii"))
                actual = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, rounds)
                return hmac.compare_digest(actual, expected)
            except (ValueError, TypeError, binascii.Error):
                return False

        return hmac.compare_digest(stored_value, plain_password)
