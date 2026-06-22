from repositories.statistics_repository import StatisticsRepository


class StatisticsService:
    def __init__(self, statistics_repository: StatisticsRepository):
        self.statistics_repository = statistics_repository

    def record_total(self, account_username: str, module: str, period_key: str, total_count: int) -> None:
        self.statistics_repository.upsert_total(account_username, module, period_key, total_count)

    def get_total(self, account_username: str, module: str, period_key: str) -> int:
        return self.statistics_repository.get_total(account_username, module, period_key)
