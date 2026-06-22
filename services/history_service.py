from models.history import HistoryRecord
from repositories.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository

    def save(self, record: HistoryRecord) -> None:
        self.history_repository.save(record)

    def list_for_account(self, account_username: str) -> list[HistoryRecord]:
        return self.history_repository.list_by_account(account_username)
