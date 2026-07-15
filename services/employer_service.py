import re
from pathlib import Path

from models.employer import Employer
from repositories.employer_repository import EmployerRepository

ACCOUNT_NUMBER_LENGTHS = {
    "sss_number": 10,
    "philhealth_number": 12,
    "hdmf_number": 12,
}


def digits_only(value: str) -> str:
    return "".join(re.findall(r"\d", str(value)))


class EmployerService:
    def __init__(self, employer_repository: EmployerRepository):
        self.repository = employer_repository

    def get_by_id(self, employer_id: int) -> Employer | None:
        return self.repository.get_by_id(employer_id)

    def list_active(self) -> list[Employer]:
        return self.repository.list_active()

    def list_all(self, include_inactive: bool = True) -> list[Employer]:
        return self.repository.list_all(include_inactive=include_inactive)

    def validate_employer_fields(
        self,
        name: str,
        sss_number: str = "",
        philhealth_number: str = "",
        hdmf_number: str = "",
    ) -> None:
        if not name.strip():
            raise ValueError("Employer name is required.")

        labels = {
            "sss_number": "SSS Number",
            "philhealth_number": "PhilHealth Number",
            "hdmf_number": "HDMF Number",
        }
        values = {
            "sss_number": sss_number,
            "philhealth_number": philhealth_number,
            "hdmf_number": hdmf_number,
        }
        for field, raw_value in values.items():
            if not raw_value:
                continue
            digits = digits_only(raw_value)
            expected = ACCOUNT_NUMBER_LENGTHS[field]
            if len(digits) != expected:
                raise ValueError(f"{labels[field]} must contain exactly {expected} digits.")

    def create_employer(
        self,
        name: str,
        address: str = "",
        tin: str = "",
        sss_number: str = "",
        philhealth_number: str = "",
        hdmf_number: str = "",
        status: str = "active",
    ) -> Employer:
        self.validate_employer_fields(name, sss_number, philhealth_number, hdmf_number)
        if self.repository.get_by_name(name):
            raise ValueError("An employer with this name already exists.")

        employer = Employer(
            name=name.strip(),
            address=address.strip(),
            tin=digits_only(tin) if tin else "",
            sss_number=digits_only(sss_number),
            philhealth_number=digits_only(philhealth_number),
            hdmf_number=digits_only(hdmf_number),
            status=status if status in {"active", "inactive"} else "active",
        )
        return self.repository.save(employer)

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
    ) -> Employer:
        existing = self.repository.get_by_id(employer_id)
        if existing is None:
            raise ValueError("Employer not found.")

        self.validate_employer_fields(name, sss_number, philhealth_number, hdmf_number)
        duplicate = self.repository.get_by_name(name)
        if duplicate is not None and duplicate.id != employer_id:
            raise ValueError("An employer with this name already exists.")

        employer = Employer(
            id=employer_id,
            name=name.strip(),
            address=address.strip(),
            tin=digits_only(tin) if tin else "",
            sss_number=digits_only(sss_number),
            philhealth_number=digits_only(philhealth_number),
            hdmf_number=digits_only(hdmf_number),
            status=status if status in {"active", "inactive"} else existing.status,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )
        return self.repository.save(employer)

    def deactivate_employer(self, employer_id: int) -> Employer:
        existing = self.repository.get_by_id(employer_id)
        if existing is None:
            raise ValueError("Employer not found.")
        existing.status = "inactive"
        return self.repository.save(existing)

    def delete_employer(self, employer_id: int) -> None:
        existing = self.repository.get_by_id(employer_id)
        if existing is None:
            raise ValueError("Employer not found.")
        if self.repository.count_accounts(employer_id) > 0:
            raise ValueError("Cannot delete an employer that is linked to accounts.")
        self.repository.delete_by_id(employer_id)

    def employer_to_session_fields(self, employer: Employer) -> dict[str, str | int]:
        return {
            "employer_id": employer.id or 0,
            "employer_name": employer.name,
            "employer_address": employer.address,
            "employer_tin": employer.tin,
            "sss_number": employer.sss_number,
            "philhealth_number": employer.philhealth_number,
            "hdmf_number": employer.hdmf_number,
        }
