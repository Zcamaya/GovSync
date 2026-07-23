# Project Navigation

This file maps the documentation set to the main folders and QA artifacts so it is easier to move between high-level guidance and source files.

## Start here

- [README.md](../README.md) — project entry point
- [docs/README.md](README.md) — canonical documentation index

## Main code areas

- [app.py](../app.py) — application startup
- [main_window.py](../main_window.py) — main shell and navigation host
- [core/](../core/) — infrastructure, wiring, session, and settings
- [controllers/](../controllers/) — UI boundary controllers
- [services/](../services/) — business logic and workflows
- [repositories/](../repositories/) — persistence layer
- [widgets/](../widgets/) — UI panels and dialogs
- [tests/](../tests/) — automated test suite

## QA and reports

- [qa_tools/](../qa_tools/) — QA runner and tooling
- [qa_output/reports/](../qa_output/reports/) — generated QA reports

## Quick QA run

Use the following command from the repository root:

```powershell
Set-Location -LiteralPath 'e:\My Program\GovSync'
$env:QT_QPA_PLATFORM='offscreen'
.\.venv\Scripts\python.exe qa_tools/qa_engine/run.py
```
