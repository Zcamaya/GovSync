from services.philhealth_service import PhilHealthService


class PhilHealthController:
    def __init__(self, service: PhilHealthService, engine=None):
        self.service = service
        self.engine = engine or self.service.create_engine()

    def list_history(self, account_username: str) -> list[dict]:
        return self.service.list_history(account_username)

    def save_history(self, account_username: str, record_data: dict) -> None:
        self.service.save_history(account_username, record_data)

    def delete_history(self, account_username: str, record_id: str) -> None:
        self.service.delete_history(account_username, record_id)

    def process(self, progress_callback=None):
        return self.service.process(self.engine, progress_callback=progress_callback)

    def get_engine(self):
        return self.engine
