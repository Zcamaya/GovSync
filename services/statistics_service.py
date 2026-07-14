from repositories.statistics_repository import StatisticsRepository


class StatisticsService:
    def __init__(self, statistics_repository: StatisticsRepository):
        self.statistics_repository = statistics_repository

    def record_total(self, account_username: str, module: str, period_key: str, total_count: int) -> None:
        self.statistics_repository.upsert_total(account_username, module, period_key, total_count)

    def get_total(self, account_username: str, module: str, period_key: str) -> int:
        return self.statistics_repository.get_total(account_username, module, period_key)

    def list_totals_for_account(self, account_username: str) -> dict[str, dict[str, int]]:
        return self.statistics_repository.list_by_account(account_username)

    def replace_totals_for_account(self, account_username: str, data: dict[str, dict[str, int]]) -> None:
        self.statistics_repository.replace_many(account_username, data)
