# Project Overview

GovSync is a desktop payroll compliance workspace for Philippine government contributions. The application focuses on SSS, PhilHealth, HDMF, payroll automation, and account-based workflow management.

## Goals

- Provide a stable desktop experience for payroll and compliance tasks.
- Keep UI, business logic, and persistence separated.
- Support multiple employer/account contexts without cross-account leakage.
- Preserve a maintainable Python/PySide6 codebase for future feature work.

## Technology stack

- Python
- PySide6 for the desktop UI
- SQLite for local persistence
- Qt-based widgets and dialogs

## Repository layout

- [app.py](../app.py) — application entry point
- [main_window.py](../main_window.py) — shell window and navigation host
- [core/](../core/) — bootstrapping, DI, navigation, settings, and session handling
- [controllers/](../controllers/) — UI-boundary orchestration
- [services/](../services/) — business rules and workflows
- [repositories/](../repositories/) — persistence operations
- [widgets/](../widgets/) — PySide6 panels and dialogs
- [storage/](../storage/) — database helpers and schema initialization

## Quick start

1. Create and activate the virtual environment.
2. Install dependencies from requirements.txt.
3. Run the application with the project entry point.
4. Use the QA tools under qa_tools/ when validating UI behavior.

## Notes

This document is the primary overview. More detailed implementation detail lives in the architecture, development rules, database, and feature documents.
