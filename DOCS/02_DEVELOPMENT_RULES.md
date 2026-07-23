# Development Rules

These rules define how GovSync should evolve over time.

## Core expectations

- Keep code readable and explicit.
- Favor small, focused modules over large catch-all files.
- Keep changes scoped to the appropriate layer.
- Update documentation when architecture or workflow changes.

## Coding standards

- Use descriptive names for functions, classes, and variables.
- Keep functions focused and avoid unnecessary indirection.
- Use type hints where practical.
- Follow the existing repository conventions for controllers, services, repositories, models, and widgets.

## Change boundaries

- Put UI layout work in widgets/.
- Put workflow logic in services/.
- Put database access in repositories/.
- Keep core wiring in core/.

## Review expectations

- Prefer small pull requests with clear intent.
- Preserve existing behavior unless a change explicitly calls for a documented adjustment.
- Avoid introducing UI redesigns without an explicit request.
- Keep tests and QA evidence aligned with the change.

## AI development guidance

- Do not introduce architectural shortcuts that bypass the existing layering.
- Do not move application code in the course of a documentation task.
- Keep documentation authoritative and avoid duplicated guidance across multiple files.
