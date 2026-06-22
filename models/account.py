from dataclasses import dataclass, field


@dataclass(slots=True)
class Account:
    username: str
    password_hash: str
    sss_number: str = ""
    philhealth_number: str = ""
    hdmf_number: str = ""
    id: int | None = None
    created_at: str | None = None
    updated_at: str | None = None
    extra: dict = field(default_factory=dict)
