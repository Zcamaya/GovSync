from dataclasses import dataclass


@dataclass(slots=True)
class Employee:
    client: str
    philhealth_number: str
    employee_name: str
    birthdate: str
