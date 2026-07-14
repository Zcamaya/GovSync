from repositories.employee_records_repository import EmployeeRecordsRepository


class EmployeeRecordsService:
    def __init__(self, repository: EmployeeRecordsRepository | None = None):
        self.repository = repository or EmployeeRecordsRepository()

    def get_statistics(self, employer_id: str | None = None) -> dict[str, object]:
        return self.repository.get_statistics(employer_id=employer_id)

    def get_filter_options(self, employer_id: str | None = None) -> dict[str, list[str]]:
        return self.repository.get_filter_options(employer_id=employer_id)

    def list_employees(
        self,
        employer_id: str | None,
        search_text: str = "",
        client_filter: str = "",
        applicable_month_filter: str = "",
        lastname_filter: str = "",
        employer_filter: str = "",
        sort_by: str = "lastname",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict], int]:
        return self.repository.list_employees(
            employer_id=employer_id,
            search_text=search_text,
            client_filter=client_filter,
            applicable_month_filter=applicable_month_filter,
            lastname_filter=lastname_filter,
            employer_filter=employer_filter,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )

    def get_employee_payroll_history(self, employer_id: str | None, employee_id: str = "", sss_number: str = "") -> list[dict]:
        return self.repository.get_employee_payroll_history(employer_id=employer_id, employee_id=employee_id, sss_number=sss_number)
