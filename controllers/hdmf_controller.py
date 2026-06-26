from services.hdmf_service import HDMFService


class HDMFController:
    def __init__(self, hdmf_service: HDMFService | None = None):
        self.hdmf_service = hdmf_service or HDMFService()

    def separate_loans(self, earnings_file, monitoring_file, progress_callback=None):
        return self.hdmf_service.separate_loans(
            earnings_file,
            monitoring_file,
            progress_callback=progress_callback,
        )

