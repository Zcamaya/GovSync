from services.hdmf_service import HDMFService


class HDMFController:
    def __init__(self, hdmf_service: HDMFService | None = None):
        self.hdmf_service = hdmf_service

    def separate_loans(self, earnings_file, monitoring_file, progress_callback=None):
        if self.hdmf_service:
            return self.hdmf_service.separate_loans(
                earnings_file,
                monitoring_file,
                progress_callback=progress_callback,
            )
        from utils.hdmf_loan_engine import separate_hdmf_loans

        return separate_hdmf_loans(
            earnings_file,
            monitoring_file,
            progress_callback=progress_callback,
        )

