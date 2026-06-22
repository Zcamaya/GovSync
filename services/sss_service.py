from utils.sss_engine import generate_sss_txt, load_sss_txt, save_sss_txt


class SSSService:
    def generate_txt(self, progress_callback=None, **kwargs):
        return generate_sss_txt(progress_callback=progress_callback, **kwargs)

    def load_txt(self, file_path):
        return load_sss_txt(file_path)

    def save_txt(self, rows, file_path):
        return save_sss_txt(rows, file_path)
