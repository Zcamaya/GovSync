# Development Guide

## Setup

1. Create and activate a virtual environment.
2. Install requirements from requirements.txt.
3. Ensure the project runs from the repository root.

## Running the app

Use the application entry point for local development.

## Testing and QA

- Use pytest for automated tests where available.
- Use the QA tools under [qa_tools/](../qa_tools/) for UI inspection and report generation.
- Keep generated QA reports under [qa_output/reports/](../qa_output/reports/).
- Use [qa_tools/qa_engine/run.py](../qa_tools/qa_engine/run.py) as a local entry point for QA runs when needed.

## Debugging

- Review the relevant widget, controller, service, and repository modules when debugging a flow.
- Use the existing logging and session handling paths for runtime issues.
- Keep changes scoped and verify the impact on the surrounding layers.
