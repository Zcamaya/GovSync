import os
from pathlib import Path


APP_NAME = "GovSync"
APP_VERSION = "2.0.0"

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"


def _default_data_dir() -> Path:
    override = os.getenv("GOVSYNC_DATA_DIR")
    if override:
        return Path(override)

    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / APP_NAME

    xdg_data_home = os.getenv("XDG_DATA_HOME")
    if xdg_data_home:
        return Path(xdg_data_home) / APP_NAME

    return Path.home() / ".local" / "share" / APP_NAME


DATA_DIR = _default_data_dir()
DATABASE_FILENAME = "govsync.db"
DATABASE_PATH = DATA_DIR / DATABASE_FILENAME
LEGACY_DATABASE_PATH = BASE_DIR / "data" / DATABASE_FILENAME
LOG_DIR = DATA_DIR / "logs"
BACKUP_DIR = DATA_DIR / "backups"

DEFAULT_THEME = "dark"
PASSWORD_MIN_LENGTH = 8
MAX_LOG_FILES = 30

SUPER_ADMIN_USERNAME = os.getenv("GOVSYNC_SUPER_ADMIN_USERNAME", "superadmin")
SUPER_ADMIN_PASSWORD = os.getenv("GOVSYNC_SUPER_ADMIN_PASSWORD", "admin1234")

DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 780
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 780
DEBUG_LAYOUT = False
