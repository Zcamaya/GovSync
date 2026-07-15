import os
import unittest

from PySide6.QtWidgets import QApplication

from widgets.auth_windows import LoginPage


class AuthUiEmployerSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_login_page_register_form_uses_employer_combo(self) -> None:
        page = LoginPage(controller=None, employer_controller=None)
        self.assertTrue(hasattr(page, "register_employer_combo"))
        self.assertTrue(page.register_employer_combo is not None)

    def test_login_page_register_form_does_not_collect_account_numbers(self) -> None:
        page = LoginPage(controller=None, employer_controller=None)
        self.assertFalse(hasattr(page, "register_sss_number"))
        self.assertFalse(hasattr(page, "register_philhealth_number"))
        self.assertFalse(hasattr(page, "register_hdmf_number"))


if __name__ == "__main__":
    unittest.main()
