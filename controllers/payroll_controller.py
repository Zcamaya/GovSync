from services.payroll_service import PayrollService


class PayrollController:
    def __init__(self, payroll_service: PayrollService | None = None):
        self.payroll_service = payroll_service or PayrollService()

    def process_file(self, file_path: str, progress_callback=None):
        return self.payroll_service.process_file(
            file_path,
            progress_callback=progress_callback,
        )

