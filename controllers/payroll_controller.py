from services.payroll_service import PayrollService


class PayrollController:
    def __init__(self, payroll_service: PayrollService | None = None):
        self.payroll_service = payroll_service or PayrollService()

    def build_import_plan(self, file_path: str, applicable_month: str | None = None, progress_callback=None):
        return self.payroll_service.build_import_plan(
            file_path,
            applicable_month=applicable_month,
            progress_callback=progress_callback,
        )

    def persist_import(self, plan):
        return self.payroll_service.persist_import(plan)

    def process_file(self, file_path: str, progress_callback=None, applicable_month: str | None = None, plan=None, overwrite: bool = False, import_data: bool = True, generate_sheets: list[str] | None = None):
        return self.payroll_service.process_file(
            file_path,
            progress_callback=progress_callback,
            applicable_month=applicable_month,
            plan=plan,
            overwrite=overwrite,
            import_data=import_data,
            generate_sheets=generate_sheets,
        )

