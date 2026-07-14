from services.payroll_import_service import PayrollImportService


class PayrollImportController:
    def __init__(self, service: PayrollImportService | None = None):
        self.service = service or PayrollImportService()

    def build_import_plan(self, file_path: str, applicable_month: str, progress_callback=None):
        return self.service.build_import_plan(file_path, applicable_month, progress_callback=progress_callback)

    def persist_import(self, plan):
        return self.service.persist_import(plan)

    def import_file(self, file_path: str, applicable_month: str, progress_callback=None):
        plan = self.build_import_plan(file_path, applicable_month, progress_callback=progress_callback)
        return self.persist_import(plan)
