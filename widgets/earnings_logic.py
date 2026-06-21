"""Compatibility wrapper for the active payroll engine."""

from utils.payroll_engine import run_payroll_task


def run_payroll_process(file_path):
    """Run the payroll processing pipeline for one Excel file."""
    return run_payroll_task(file_path)
