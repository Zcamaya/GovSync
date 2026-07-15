import sqlite3
import shutil
from pathlib import Path

from config import DATABASE_PATH, LEGACY_DATABASE_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL DEFAULT '',
    tin TEXT NOT NULL DEFAULT '',
    sss_number TEXT NOT NULL DEFAULT '',
    philhealth_number TEXT NOT NULL DEFAULT '',
    hdmf_number TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    sss_number TEXT NOT NULL DEFAULT '',
    philhealth_number TEXT NOT NULL DEFAULT '',
    hdmf_number TEXT NOT NULL DEFAULT '',
    employer_id INTEGER,
    employer_name TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(employer_id) REFERENCES employers(id)
);

CREATE TABLE IF NOT EXISTS history_records (
    id TEXT PRIMARY KEY,
    account_username TEXT NOT NULL,
    module TEXT NOT NULL,
    period_label TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_username TEXT NOT NULL,
    module TEXT NOT NULL,
    period_key TEXT NOT NULL,
    total_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_username, module, period_key)
);

"""


def database_path() -> Path:
    return DATABASE_PATH


def _migrate_legacy_database(target_path: Path) -> None:
    if target_path.exists() or not LEGACY_DATABASE_PATH.exists():
        return

    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY_DATABASE_PATH, target_path)


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = Path(path or database_path())
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_account_columns(connection: sqlite3.Connection) -> None:
    columns = {row[1] for row in connection.execute("PRAGMA table_info(accounts)")}
    if "employer_id" not in columns:
        connection.execute("ALTER TABLE accounts ADD COLUMN employer_id INTEGER")
    if "employer_name" not in columns:
        connection.execute("ALTER TABLE accounts ADD COLUMN employer_name TEXT NOT NULL DEFAULT ''")


def _backfill_employer_links(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON")
    employer_rows = connection.execute(
        "SELECT id, name FROM employers"
    ).fetchall()
    employer_names = {row[1].strip().lower(): row[0] for row in employer_rows if row[1]}

    account_rows = connection.execute(
        "SELECT id, username, employer_name, employer_id FROM accounts"
    ).fetchall()
    for account in account_rows:
        existing_employer_id = account["employer_id"]
        employer_name = str(account["employer_name"] or "").strip()
        if existing_employer_id is None:
            if employer_name:
                normalized_name = employer_name.strip().lower()
                if normalized_name in employer_names:
                    existing_employer_id = employer_names[normalized_name]
                else:
                    cursor = connection.execute(
                        "INSERT INTO employers (name, status) VALUES (?, 'active')",
                        (employer_name,),
                    )
                    existing_employer_id = cursor.lastrowid
                    employer_names[normalized_name] = existing_employer_id
            else:
                cursor = connection.execute(
                    "INSERT INTO employers (name, status) VALUES (?, 'active')",
                    (f"Employer {account['username']}",),
                )
                existing_employer_id = cursor.lastrowid
        if existing_employer_id is not None:
            connection.execute(
                "UPDATE accounts SET employer_id = ? WHERE id = ?",
                (existing_employer_id, account["id"]),
            )


def initialize_database(path: Path | None = None) -> None:
    target_path = Path(path or database_path())
    _migrate_legacy_database(target_path)
    with connect(target_path) as connection:
        connection.executescript(SCHEMA)
        _ensure_account_columns(connection)
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_accounts_employer_id ON accounts(employer_id)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_employers_status ON employers(status)"
        )
        _backfill_employer_links(connection)
        connection.commit()
