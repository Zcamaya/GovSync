from utils.payroll_engine import run_payroll_task


class PayrollService:
    def process_file(self, file_path: str, progress_callback=None):
        return run_payroll_task(file_path)
