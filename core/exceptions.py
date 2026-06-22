class GovSyncError(Exception):
    """Base exception for GovSync."""


class AuthenticationError(GovSyncError):
    """Raised when authentication fails."""


class ValidationError(GovSyncError):
    """Raised when incoming data is invalid."""


class StorageError(GovSyncError):
    """Raised when persistence fails."""


class HistoryError(GovSyncError):
    """Raised when history processing fails."""


class ExcelFormatError(GovSyncError):
    """Raised when an uploaded workbook is not usable."""


class PayrollError(GovSyncError):
    """Raised when payroll processing fails."""
