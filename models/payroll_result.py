from dataclasses import dataclass, field


@dataclass(slots=True)
class PayrollResult:
    success: bool
    message: str
    output_path: str = ""
    records_written: int = 0
    metadata: dict = field(default_factory=dict)
