from pathlib import Path

from core.settings import Settings


class StorageService:
    """Centralizes filesystem paths for imports, exports, reports, and backups."""

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def data_dir(self) -> Path:
        path = Path(self.settings.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def import_dir(self) -> Path:
        path = self.data_dir / "imports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def export_dir(self) -> Path:
        path = self.data_dir / "exports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def report_dir(self) -> Path:
        path = self.data_dir / "reports"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def backup_dir(self) -> Path:
        path = Path(self.settings.backup_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def account_dir(self, username: str) -> Path:
        safe_name = "".join(char if char.isalnum() or char in "._-" else "_" for char in username.strip() or "default")
        path = self.data_dir / "accounts" / safe_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def validate_network_path(self, path: Path | str) -> bool:
        candidate = Path(path)
        try:
            if not candidate.exists():
                return False
            test_file = candidate / ".govsync_path_check"
            test_file.touch(exist_ok=True)
            test_file.unlink(missing_ok=True)
            return True
        except OSError:
            return False
