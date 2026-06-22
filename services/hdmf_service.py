from utils.hdmf_loan_engine import separate_hdmf_loans


class HDMFService:
    def separate_loans(self, earnings_file, monitoring_file, progress_callback=None):
        return separate_hdmf_loans(
            earnings_file,
            monitoring_file,
            progress_callback=progress_callback,
        )
