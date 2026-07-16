import unittest

from models.account import Account
import services.auth_manager as auth_manager


class AuthManagerAccountPayloadTests(unittest.TestCase):
    def test_account_to_dict_preserves_account_fields(self) -> None:
        account = Account(
            username="demo",
            password_hash="hash123",
            sss_number="1234567890",
            philhealth_number="123456789012",
            hdmf_number="123456789012",
            employer_id=7,
            employer_name="Acme Corp",
        )

        payload = auth_manager._account_to_dict(account)

        self.assertEqual(payload["username"], "demo")
        self.assertEqual(payload["password"], "hash123")
        self.assertEqual(payload["password_hash"], "hash123")
        self.assertEqual(payload["sss_number"], "1234567890")
        self.assertEqual(payload["philhealth_number"], "123456789012")
        self.assertEqual(payload["hdmf_number"], "123456789012")
        self.assertEqual(payload["employer_id"], 7)
        self.assertEqual(payload["employer_name"], "Acme Corp")


if __name__ == "__main__":
    unittest.main()
