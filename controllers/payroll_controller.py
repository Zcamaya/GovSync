from services.payroll_service import PayrollService


class PayrollController:
    def __init__(self, payroll_service: PayrollService | None = None):
        self.payroll_service = payroll_service

    def process_file(self, file_path: str, progress_callback=None):
        if self.payroll_service:
            return self.payroll_service.process_file(
                file_path,
                progress_callback=progress_callback,
            )
        from utils.payroll_engine import run_payroll_task

        return run_payroll_task(file_path)

