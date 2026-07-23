"# GovSync

GovSync is a desktop payroll compliance workspace for Philippine government contributions, with modular workflows for SSS, PhilHealth, HDMF, and payroll automation.

## Highlights

- Account registration now associates each account with a normalized employer record instead of duplicating employer details in the account payload.
- SSS, HDMF, and PhilHealth panels reset their state when switching accounts to prevent stale or cross-account data from leaking into the UI.
- PhilHealth history and deletion actions are scoped to the active account.
- The existing UI is preserved while the underlying logic and persistence are improved.

## Documentation

- [docs/README.md](docs/README.md) for the canonical documentation index.
- [docs/00_PROJECT_OVERVIEW.md](docs/00_PROJECT_OVERVIEW.md) for the project overview.
- [docs/01_ARCHITECTURE.md](docs/01_ARCHITECTURE.md) for the current architecture.
- [docs/02_DEVELOPMENT_RULES.md](docs/02_DEVELOPMENT_RULES.md) for development guidance.
- [docs/06_DEVELOPMENT_GUIDE.md](docs/06_DEVELOPMENT_GUIDE.md) for setup, testing, and QA guidance.
- [CHANGELOG.md](CHANGELOG.md) for feature and maintenance history.

Historical and task-specific documents are preserved in [docs/archive/README.md](docs/archive/README.md).

## Repository Hygiene

- Generated build artifacts are ignored via `.gitignore`.
- AI tooling should also skip generated and local environment files using `.aiignore`.
