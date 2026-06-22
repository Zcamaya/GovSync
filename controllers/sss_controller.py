from services.sss_service import SSSService


class SSSController:
    def __init__(self, sss_service: SSSService | None = None):
        self.sss_service = sss_service

    def generate_txt(self, progress_callback=None, **kwargs):
        if self.sss_service:
            return self.sss_service.generate_txt(progress_callback=progress_callback, **kwargs)
        from utils.sss_engine import generate_sss_txt

        return generate_sss_txt(progress_callback=progress_callback, **kwargs)

    def load_txt(self, file_path):
        if self.sss_service:
            return self.sss_service.load_txt(file_path)
        from utils.sss_engine import load_sss_txt

        return load_sss_txt(file_path)

    def save_txt(self, rows, file_path):
        if self.sss_service:
            return self.sss_service.save_txt(rows, file_path)
        from utils.sss_engine import save_sss_txt

        return save_sss_txt(rows, file_path)

