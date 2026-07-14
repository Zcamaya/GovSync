from services.payroll_service import PayrollService


class FakeImportController:
    def __init__(self):
        self.calls = []

    def import_file(self, file_path, applicable_month, progress_callback=None):
        self.calls.append((file_path, applicable_month, progress_callback))
        return {"ok": True}


def test_payroll_service_import_file_forwards_to_controller_with_default_month():
    controller = FakeImportController()
    service = PayrollService(import_controller=controller)

    result = service.import_file("sample.xlsx", applicable_month=None, progress_callback="cb")

    assert result == {"ok": True}
    assert controller.calls == [("sample.xlsx", "", "cb")]
