QA Engine
=========

Purpose
-------
A lightweight, automated QA engine for the GovSync PySide6 application. It discovers the running UI, collects layout/accessibility/performance data, captures screenshots, and emits JSON and markdown reports to `qa_output/reports`.

Quick start
-----------
1. Activate the repository virtualenv:

```powershell
& "e:/My Program/GovSync/.venv/Scripts/Activate.ps1"
```

2. Run the QA engine from the project root:

```powershell
& "e:/My Program/GovSync/.venv/Scripts/python.exe" tools/qa_engine/run.py
```

Outputs
-------
- `qa_output/screenshots` — PNG screenshots captured during runs.
- `qa_output/reports` — JSON and markdown reports summarizing findings.

Extending
---------
Add new inspector modules under `tools/qa_engine`, expose them in `run.py`, and append their outputs to the report writer.

Notes
-----
- The engine uses Qt offscreen mode by default; ensure `QT_QPA_PLATFORM` is `offscreen` when running headless.
- For visual diffing, add reference screenshots into `qa_output/screenshots/baseline` and run the comparator.
