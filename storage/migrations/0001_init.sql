CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    sss_number TEXT NOT NULL DEFAULT '',
    philhealth_number TEXT NOT NULL DEFAULT '',
    hdmf_number TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
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
