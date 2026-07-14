from dataclasses import dataclass, field
from typing import Any


@dataclass
class PayrollImport:
    id: str
    employer_id: str
    applicable_month: str
    from_date: str
    to_date: str
    client_id: str
    client_name: str
    employee_count: int
    original_filename: str
    file_hash: str
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class PayrollRecord:
    id: str
    import_id: str
    batchid: str = ""
    fdate: str = ""
    tdate: str = ""
    custid: str = ""
    company: str = ""
    emplid: str = ""
    lastname: str = ""
    firstname: str = ""
    middlename: str = ""
    suffix: str = ""
    birthdate: str = ""
    basicrate: str = ""
    billrate: str = ""
    sssno: str = ""
    sss: str = ""
    eeshare: str = ""
    ershare: str = ""
    sssrem: str = ""
    er: str = ""
    pagibigno: str = ""
    pagibig: str = ""
    pagibigrem: str = ""
    phealthno: str = ""
    phealth: str = ""
    phealthrem: str = ""
    sssloan: str = ""
    pbigloan: str = ""
    ctr: str = ""
    tinno: str = ""
    datehired: str = ""
    companyid: str = ""
    position: str = ""


@dataclass
class PayrollImportPlan:
    import_id: str
    file_hash: str
    employer_id: str
    applicable_month: str
    from_date: str
    to_date: str
    client_id: str
    client_name: str
    employee_count: int
    original_filename: str
    records: list[dict[str, Any]] = field(default_factory=list)
    existing_import: dict[str, Any] | None = None
    existing_payroll: dict[str, Any] | None = None
