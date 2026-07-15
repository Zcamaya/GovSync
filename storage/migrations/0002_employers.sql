CREATE TABLE IF NOT EXISTS employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    tin TEXT NOT NULL DEFAULT '',
    sss_number TEXT NOT NULL DEFAULT '',
    philhealth_number TEXT NOT NULL DEFAULT '',
    hdmf_number TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_employers_status ON employers(status);
CREATE INDEX IF NOT EXISTS idx_employers_name ON employers(name);
