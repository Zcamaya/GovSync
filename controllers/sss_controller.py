from services.sss_service import SSSService


class SSSController:
    def __init__(self, sss_service: SSSService | None = None):
        self.sss_service = sss_service or SSSService()

    def generate_txt(self, progress_callback=None, **kwargs):
        return self.sss_service.generate_txt(progress_callback=progress_callback, **kwargs)

    def load_txt(self, file_path):
        return self.sss_service.load_txt(file_path)

    def save_txt(self, rows, file_path):
        return self.sss_service.save_txt(rows, file_path)

