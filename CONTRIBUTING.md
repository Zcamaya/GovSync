# Contributing to GovSync

Thank you for helping improve GovSync. This document describes the process for contributing, reporting issues, and submitting code changes.

## How to contribute

1. Fork the repository.
2. Create a branch named for your change:
   - `feature/<short-description>`
   - `fix/<short-description>`
   - `refactor/<short-description>`
3. Make your changes and keep commits small and focused.
4. Run the existing validation steps before submitting a pull request.
5. Open a pull request against the main branch with a clear description of the change.

## Development workflow

- Use the existing package structure:
  - `controllers/` for UI boundary controllers
  - `services/` for business logic
  - `repositories/` for data access
  - `widgets/` for UI components
  - `core/` for application wiring and infrastructure
- Prefer dependency injection via the `core/dependency_container.py` and service/controller constructors.
- Avoid direct business logic in widgets.
- Keep legacy module references out of new code.

## Testing and validation

- Run Python syntax checks with `python -m py_compile`.
- Ensure changes do not introduce direct `utils.*` imports for migrated functionality.
- Maintain or update `RESTRUCTURE_PLAN.md` if the change affects the migration roadmap.

## Code style

- Use clear, explicit imports.
- Keep functions and classes names descriptive.
- Use `snake_case` for functions and variables, `PascalCase` for classes.
- Keep line lengths readable and maintain consistent formatting.

## Reporting issues

- Open a GitHub issue with a descriptive title and clear reproduction steps.
- Include any error messages or stack traces.
- If requesting a feature, explain the intended workflow and expected result.

## Notes

- This repository is a desktop application built with PySide6.
- The codebase is organized into feature-specific services and controllers.
- Legacy migration work is tracked in `RESTRUCTURE_PLAN.md`.
