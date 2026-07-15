from services.employer_service import EmployerService


class EmployerController:
    def __init__(self, employer_service: EmployerService):
        self.employer_service = employer_service

    def list_active_employers(self):
        return self.employer_service.list_active()

    def list_all_employers(self, include_inactive: bool = True):
        return self.employer_service.list_all(include_inactive=include_inactive)

    def create_employer(
        self,
        name: str,
        address: str = "",
        tin: str = "",
        sss_number: str = "",
        philhealth_number: str = "",
        hdmf_number: str = "",
        status: str = "active",
    ):
        return self.employer_service.create_employer(
            name=name,
            address=address,
            tin=tin,
            sss_number=sss_number,
            philhealth_number=philhealth_number,
            hdmf_number=hdmf_number,
            status=status,
        )

    def update_employer(
        self,
        employer_id: int,
        name: str,
        address: str = "",
        tin: str = "",
        sss_number: str = "",
        philhealth_number: str = "",
        hdmf_number: str = "",
        status: str = "active",
    ):
        return self.employer_service.update_employer(
            employer_id=employer_id,
            name=name,
            address=address,
            tin=tin,
            sss_number=sss_number,
            philhealth_number=philhealth_number,
            hdmf_number=hdmf_number,
            status=status,
        )

    def deactivate_employer(self, employer_id: int):
        return self.employer_service.deactivate_employer(employer_id)

    def delete_employer(self, employer_id: int):
        self.employer_service.delete_employer(employer_id)

    def get_employer(self, employer_id: int):
        return self.employer_service.get_by_id(employer_id)
