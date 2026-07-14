"# GovSync

GovSync is a desktop payroll compliance workspace for Philippine government contributions, with modular workflows for SSS, PhilHealth, HDMF, and payroll automation.

## Highlights

- Account registration and persistence now capture an employer name for multi-employer support.
- SSS, HDMF, and PhilHealth panels reset their state when switching accounts to prevent stale or cross-account data from leaking into the UI.
- PhilHealth history and deletion actions are scoped to the active account.
- The existing UI is preserved while the underlying logic and persistence are improved.

## Documentation

- [AI_CONTEXT.md](AI_CONTEXT.md) for architecture and handoff notes.
- [PROJECT_RULES.md](PROJECT_RULES.md) for development and architecture guidelines.
- [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) for the current design overview.
- [CHANGELOG.md](CHANGELOG.md) for feature and maintenance history.

## Repository Hygiene

- Generated build artifacts are ignored via `.gitignore`.
- AI tooling should also skip generated and local environment files using `.aiignore`.
