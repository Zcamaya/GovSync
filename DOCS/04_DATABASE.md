# Database

GovSync uses a local SQLite persistence layer for accounts, history, statistics, and related workflow data.

## Storage responsibilities

- [storage/sqlite.py](../storage/sqlite.py) handles connection helpers and schema initialization.
- [repositories/](../repositories/) provide CRUD-style access around the database.
- [services/](../services/) use repositories to perform higher-level workflow operations.

## Data concerns

- Accounts store authentication and account identity information.
- History records capture workflow activity and audit context.
- Statistics data supports dashboard and reporting flows.

## Data access guidance

- Keep repositories focused on persistence and simple query logic.
- Avoid moving business validation into repositories.
- Keep schema initialization centralized.
- Treat database lifecycle and cleanup carefully during tests.
