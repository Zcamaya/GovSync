from dataclasses import dataclass


@dataclass(slots=True)
class Employer:
    name: str
    address: str = ""
    tin: str = ""
    sss_number: str = ""
    philhealth_number: str = ""
    hdmf_number: str = ""
    status: str = "active"
    id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
