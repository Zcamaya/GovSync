# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Added employer selection during account creation so users can associate accounts with normalized employer records.
- Persisted employer links in account storage, registration forms, and account listings while preserving employer-name compatibility data.
- Improved account switching isolation across SSS, HDMF, and PhilHealth panels by resetting stale UI state and clearing form fields.
- Scoped PhilHealth history and delete actions to the active account to prevent cross-account data leakage.
- Added regression tests covering employer-name persistence and account-scoped panel behavior.
- Updated project documentation to keep the handoff notes and contribution guidance aligned with the current system behavior.
- Migrated legacy `utils/` engines into the `services/` package.
- Replaced legacy `utils` imports with service/core/shared equivalents.
- Removed `utils/` package after successful migration.
- Added `CONTRIBUTING.md` for development guidelines.

## [0.1.0] - 2026-06-26

- Initial project scaffold and refactor plan.
