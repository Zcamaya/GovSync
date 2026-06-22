from services.philhealth_service import PhilHealthService
from utils import philhealth_engine


class PhilHealthController:
    def __init__(self, service: PhilHealthService):
        self.service = service
        self.engine = philhealth_engine.PhicExtractorApp()

    def list_history(self, account_username: str) -> list[dict]:
        return self.service.list_history(account_username)

    def save_history(self, account_username: str, record_data: dict) -> None:
        self.service.save_history(account_username, record_data)

    def delete_history(self, record_id: str) -> None:
        self.service.delete_history(record_id)

    def process(self, progress_callback=None):
        return self.engine.process_files(progress_callback=progress_callback)

    def get_engine(self):
        return self.engine
