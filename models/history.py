from dataclasses import dataclass, field


@dataclass(slots=True)
class HistoryRecord:
    id: str
    account_username: str
    module: str
    period_label: str
    payload_json: str
    created_at: str | None = None
    extra: dict = field(default_factory=dict)
