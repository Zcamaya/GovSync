import gc
import tempfile
import unittest
from pathlib import Path

import config
import services.auth_manager as auth_manager
import storage.sqlite as sqlite_storage
from repositories.employer_repository import EmployerRepository


class AuthEmployerNameTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_govsync.sqlite"
        config.DATABASE_PATH = self.db_path
        sqlite_storage.DATABASE_PATH = self.db_path
        auth_manager._account_repository = None
        auth_manager._auth_service = None

    def tearDown(self) -> None:
        auth_manager._account_repository = None
        auth_manager._auth_service = None
        gc.collect()
        self.temp_dir.cleanup()

    def test_register_account_creates_employer_and_links_account(self) -> None:
        account = auth_manager.register_account(
            username="employer-user",
            password="secret123",
            employer_name="Acme Corp",
        )

        self.assertIsNotNone(account.employer_id)
        self.assertEqual(account.employer_name, "Acme Corp")

        saved_account = auth_manager.get_account("employer-user")
        self.assertIsNotNone(saved_account)
        self.assertEqual(saved_account["employer_id"], account.employer_id)
        self.assertEqual(saved_account["employer_name"], "Acme Corp")

        employer_repository = EmployerRepository(self.db_path)
        employer = employer_repository.get_by_id(account.employer_id)
        self.assertIsNotNone(employer)
        self.assertEqual(employer.name, "Acme Corp")


if __name__ == "__main__":
    unittest.main()
