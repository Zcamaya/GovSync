from controllers.payroll_import_controller import PayrollImportController
from services.payroll_engine import run_payroll_task


class PayrollService:
    def __init__(self, import_controller: PayrollImportController | None = None):
        self.import_controller = import_controller or PayrollImportController()

    def build_import_plan(self, file_path: str, applicable_month: str | None = None, progress_callback=None):
        if applicable_month is None:
            applicable_month = ""
        return self.import_controller.build_import_plan(file_path, applicable_month, progress_callback=progress_callback)

    def persist_import(self, plan):
        return self.import_controller.persist_import(plan)

    def import_file(self, file_path: str, applicable_month: str | None = None, progress_callback=None):
        normalized_month = applicable_month or ""
        return self.import_controller.import_file(file_path, normalized_month, progress_callback=progress_callback)

    def process_file(self, file_path: str, progress_callback=None, applicable_month: str | None = None, plan=None, overwrite: bool = False, import_data: bool = True, generate_sheets: list[str] | None = None):
        if applicable_month is None:
            applicable_month = ""
        if not import_data:
            return run_payroll_task(file_path, selected_sheets=generate_sheets)
        if plan is None:
            plan = self.build_import_plan(file_path, applicable_month, progress_callback=progress_callback)
        if (plan.existing_import is not None or plan.existing_payroll is not None) and not overwrite:
            return False, "Skipped because the workbook or payroll already exists.", 0
        self.persist_import(plan)
        return run_payroll_task(file_path, selected_sheets=generate_sheets)
