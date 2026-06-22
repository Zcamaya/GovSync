from dataclasses import dataclass
from pathlib import Path

import config as app_config


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    base_dir: Path
    data_dir: Path
    database_path: Path
    log_dir: Path
    backup_dir: Path
    theme: str


def load_settings() -> Settings:
    return Settings(
        app_name=app_config.APP_NAME,
        app_version=app_config.APP_VERSION,
        base_dir=app_config.BASE_DIR,
        data_dir=app_config.DATA_DIR,
        database_path=app_config.DATABASE_PATH,
        log_dir=app_config.LOG_DIR,
        backup_dir=app_config.BACKUP_DIR,
        theme=app_config.DEFAULT_THEME,
    )
