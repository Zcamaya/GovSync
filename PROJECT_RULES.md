# PROJECT_RULES.md

## 1. Project Philosophy

- Design philosophy
  - Keep the application modular and layered.
  - Separate UI, orchestration, business logic, and persistence clearly.
  - Prefer explicit wiring over hidden global state.
  - Keep code readable and easy to navigate by another AI or developer.

- Long-term goals
  - Build a stable payroll compliance workspace that can grow with new government modules.
  - Keep UI and backend decoupled so new features can be added without breaking existing layers.
  - Maintain a reliable local persistence layer for account, history, and statistics data.

- Maintainability goals
  - Keep each file focused on one responsibility.
  - Document architecture and rules in `PROJECT_RULES.md` and `AI_CONTEXT.md`.
  - Update rules and architecture documentation whenever the code structure changes.
- Keep `.gitignore` and `.aiignore` up to date so generated output, local environments, and editor metadata are excluded from both source control and AI edits.
- Scalability goals
  - Keep services stateless when possible and inject dependencies through `core/dependency_container.py`.
  - Keep repositories thin so persistence can evolve without affecting business logic.
  - Avoid adding UI-specific logic outside `widgets/`.

- Readability goals
  - Use descriptive names, consistent formatting, and small reusable components.
  - Keep widget layouts clear and maintain shared style constants.
  - Prefer explicit method names and avoid clever one-liners.

---

## 2. Architecture Rules

### Architecture pattern

This repository uses a layered architecture:

UI
↓
Controller
↓
Service
↓
Repository
↓
Database

### Responsibilities of each layer

- UI / widgets:
  - Build PySide6 widgets, dialogs, and layouts.
  - Emit signals for user actions.
  - Receive and display data.
  - Do not perform business logic or direct persistence.

- Controllers:
  - Coordinate between widgets and services.
  - Remain thin and translate UI events into service calls.
  - Do not contain core business logic.

- Services:
  - Implement business rules, validation, and processing workflows.
  - Use repositories for persistence and engines for file processing.
  - Do not create UI elements.

- Repositories:
  - Encapsulate SQLite access and CRUD operations.
  - Expose simple persistence methods for services.
  - Do not contain business validation or UI code.

- Database / storage:
  - Provide connection helpers and schema initialization.
  - Do not perform higher-level logic.

### Allowed dependencies

- Widget → Controller
- Controller → Service
- Service → Repository
- Repository → Database / storage
- Shared utilities can be used by any layer if they are layer-agnostic.

### Forbidden dependencies

- Widget → Repository
- Widget → Database / storage
- Service → Widget
- Repository → Widget
- Controller → Database / storage directly
- Widgets should not import repository modules directly except for pure UI helpers.

---

## 3. Folder Rules

- `app.py`
  - Application launch and startup behavior only.
  - Should not contain business logic.

- `config.py`
  - Global constants, directory paths, environment overrides.
  - Only runtime configuration values.

- `core/`
  - Application bootstrap, dependency container, navigation, session, and logger setup.
  - Allowed: DI wiring, app lifecycle control, central settings, navigation orchestration.
  - Forbidden: business processing or UI element creation beyond control flow.

- `controllers/`
  - Mediators between widgets and services.
  - Allowed: orchestration, thin adaptation, forwarding calls.
  - Forbidden: data persistence logic, UI layout logic, heavy business rules.

- `services/`
  - Business logic, file processing workflows, validation, engine orchestration.
  - Allowed: algorithmic work, input validation, data transformation.
  - Forbidden: creating Qt widgets or directly manipulating the database schema.

- `repositories/`
  - Data access and persistence operations.
  - Allowed: SQL queries, connection handling, CRUD.
  - Forbidden: business validation beyond basic consistency, UI interaction.

- `models/`
  - Data classes and DTOs.
  - Allowed: simple typed containers and `dataclass` definitions.
  - Forbidden: behavior-heavy methods, persistence logic, UI code.

- `widgets/`
  - PySide6 UI components and panels.
  - Allowed: Qt widget creation, layout, styling, signals.
  - Forbidden: persistence logic, repository imports, business rules.

- `shared/`
  - Reusable UI utilities, resource helpers, and constants.
  - Allowed: icon helpers, path helpers, style utilities.
  - Forbidden: business or persistence logic unless truly shared.

- `storage/`
  - Database connection helpers and schema initialization.
  - Allowed: SQLite setup and migration logic.
  - Forbidden: service-level workflows.

- `constants/`
  - Styling aliases and constant exports.
  - Allowed: style classes and shared constant bundles.
  - Forbidden: runtime logic.

- `assets/`
  - Static resources only: icons, SVGs, images.

- `build/` and `dist/`
  - Build artifacts only.
  - Do not commit generated files unless required.

---

## 4. File Rules

### Controller files

Allowed:
- Coordinate UI requests.
- Call service methods.
- Translate widget events into business operations.
- Return results to UI.

Forbidden:
- SQL or direct database access.
- Creating Qt widgets.
- Implementing core business logic.
- Persisting state directly.

### Service files

Allowed:
- Business rules and validation.
- Data transformation and processing.
- File processing engines and workflows.
- Calling repository methods.

Forbidden:
- UI creation or Qt code.
- Direct SQL outside repositories.
- Importing widgets.

### Repository files

Allowed:
- SQLite queries and connection handling.
- CRUD and persistence methods.
- Schema-safe operations.

Forbidden:
- UI code.
- Business logic beyond persistence.
- Direct use of services.

### Model files

Allowed:
- Data classes and typed DTOs.
- Simple conversion helpers.

Forbidden:
- Persistence operations.
- UI or widget behavior.
- Complex business processing.

### Widget files

Allowed:
- Qt widget construction.
- Layouts, styling, signals, and event handling.
- Calling controllers or emitting signals.

Forbidden:
- Accessing repositories or database.
- Implementing business logic beyond display state.
- Importing services directly unless only for display helpers.

### Utility/helper files

Allowed:
- Shared functions for paths, resources, icons, and styles.
- Cross-layer helper logic that is non-business.

Forbidden:
- Layer-specific business rules.
- Service-like persistence or UI creation.

---

## 5. Naming Conventions

- File naming
  - Use lowercase with underscores for Python file names.
  - Example: `payroll_service.py`, `auth_controller.py`.

- Folder naming
  - Use lowercase with underscores for folders.
  - Example: `core/`, `widgets/`, `services/`.

- Class naming
  - Use `PascalCase` for classes and dataclasses.
  - Example: `MainWindow`, `AccountRepository`.

- Method naming
  - Use `snake_case` for methods and functions.
  - Example: `create_main_window`, `list_by_account`.

- Variable naming
  - Use `snake_case` for variables.
  - Use descriptive names.

- Constant naming
  - Use `UPPER_CASE_WITH_UNDERSCORES`.
  - Example: `APP_NAME`, `DEFAULT_WINDOW_WIDTH`.

- Signal naming
  - Use descriptive, snake_case names with verbs.
  - Example: `logout_requested`, `delete_requested`, `finished`.

- Resource naming
  - Use descriptive filenames for assets and resources.
  - Example: `logo.svg`, `icon.ico`, `exit.svg`.

---

## 6. UI Standards

- Layout spacing
  - Use consistent margins around 10-20 pixels.
  - Keep components aligned and spaced with `QVBoxLayout`/`QHBoxLayout`.

- Margins
  - Use `setContentsMargins(10, 10, 10, 10)` or similar consistent values.

- Fonts
  - Prefer `Segoe UI`.
  - Use bold text for headings and labels.

- Colors
  - Use the dark theme palette already present: dark backgrounds with teal/green/blue accent colors.
  - Keep text high contrast on dark surfaces.

- Button styles
  - Use shared style classes or stylesheet constants.
  - Primary actions should be visually distinct.

- Dialog styles
  - Use frameless custom dialogs where defined (`GlassDialog`).
  - Keep dialogs readable and consistent.

- Icons
  - Use SVG icons and `shared.ui.icon_utils` helpers.
  - Keep icon color and size consistent with styling.

- Glass panels
  - Use `TrueGlassPanel` for translucent containers and shared glass style.

- Reusable widgets
  - Avoid duplicating layout styles.
  - Build helpers for repeated panels or controls.

---

## 7. Coding Standards

- Function length
  - Prefer functions under 50 lines.
  - Split long methods into private helpers.

- Class size
  - Keep classes focused; avoid classes that do too much.
  - Prefer composition and reusable subcomponents.

- File size
  - Keep files readable; if a file grows too large, split related logic.

- Documentation style
  - Use inline comments sparingly.
  - Prefer clear code over comments.
  - Add docstrings for non-obvious classes and functions.

- Type hints
  - Use type hints where practical.
  - Prefer typed dataclasses and method signatures.

- Error handling
  - Catch exceptions at integration boundaries.
  - Use user-friendly messages in UI dialogs.
  - Log errors via `core.logger` when appropriate.

- Logging
  - Configure logging in `core/logger.py`.
  - Use logger objects in services and core modules.

- Comments
  - Keep comments concise and meaningful.
  - Do not comment obvious code.

- Exception handling
  - Use custom exceptions where meaningful (e.g., `AuthenticationError`).
  - Avoid broad exception swallowing without logging.

---

## 8. SOLID Principles

- Single Responsibility
  - Each file and class should have one reason to change.
  - `widgets/` should handle only UI.
  - `services/` should handle only business logic.

- Open/Closed
  - Add new behavior through new services or controllers rather than modifying existing core structures where possible.

- Liskov Substitution
  - Use interfaces and abstractions when swapping implementations.

- Interface Segregation
  - Keep controllers and services small and focused.

- Dependency Inversion
  - Depend on abstractions and inject dependencies through `core/dependency_container.py`.

### Recommendations for violations

- If a widget imports a repository directly, refactor it to use a controller or service.
- If business logic appears in UI code, move it into a service.
- If persistence logic appears outside repositories, move it into repository methods.

---

## 9. Clean Code Rules

- No duplicated code.
- Avoid magic numbers; use named constants instead.
- Prefer composition over inheritance when adding behavior.
- Keep functions small and focused.
- Use descriptive names.
- Remove dead code only when safe.
- Keep modules loosely coupled.
- Favor readability over clever code.

---

## 10. Dependency Rules

Allowed:
- Widget → Controller
- Controller → Service
- Service → Repository
- Repository → Database / storage
- Shared utilities may be used by any layer if layer-agnostic.

Forbidden:
- Widget → Repository
- Widget → Database / storage
- Service → Widget
- Repository → Widget
- Controller → Database / storage directly

---

## 11. Refactoring Rules

- Never change behavior unless requested.
- Preserve backward compatibility.
- Refactor incrementally.
- Improve readability.
- Reduce coupling.
- Increase cohesion.
- Avoid unnecessary rewrites.

---

## 12. Development Workflow

Before coding:
1. Read `PROJECT_RULES.md`.
2. Read `AI_CONTEXT.md`.
3. Read `CURRENT_TASK.md` if present; otherwise infer task from `AI_CONTEXT.md`.

Before finishing:
- Verify imports.
- Run basic validation or tests if available.
- Remove unused code if safe.
- Update documentation.
- Update `PROJECT_RULES.md` if conventions or architecture evolve.

---

## 13. AI Behavior Rules

- Understand the architecture before coding.
- Modify only relevant files.
- Avoid unrelated refactors.
- Preserve existing functionality.
- Explain significant architectural changes before implementing them.
- Ask for clarification if requirements are ambiguous.
- Prefer improving existing code over rewriting it.

---

## 14. Code Review Checklist

- [ ] Architecture preserved
- [ ] No duplicate logic
- [ ] No unnecessary dependencies
- [ ] No unused imports
- [ ] Proper naming
- [ ] Business logic remains outside the UI
- [ ] Controllers remain thin
- [ ] Services contain business logic
- [ ] Repositories only access data
- [ ] Documentation updated

---

## 15. Permanent Project Rules

- Never access the database directly from UI code.
- Never place business logic inside widgets.
- Keep reusable components generic.
- Use dependency injection whenever practical.
- Keep the application modular.
- Keep the project easy for another AI or developer to continue.
- Update this file when the project architecture or conventions change.
