# AI_CONTEXT.md

## 1. Project Overview

- Project name: GovSync
- Purpose: A desktop payroll compliance workspace for Philippine government contributions (SSS, PhilHealth, HDMF) and payroll automation.
- Target users: Payroll officers, HR administrators, accounting staff, and government compliance teams.
- Main features:
  - Single-instance desktop application using PySide6 UI.
  - Login flow with super-admin and normal account handling.
  - Account creation captures an employer name so the workspace can support multiple employers and users.
  - Account switching resets panel state and clears stale form fields to prevent cross-account leakage.
  - Dashboard workspace with modules for Earnings, PhilHealth, HDMF, SSS, and HDMF Loan processing.
  - Payroll and contribution file automation, file generation, historical record tracking, and statistics storage.
  - Local SQLite persistence for accounts, history records, and statistics.
- Current development status:
  - Stable UI flow exists for login and main application pages.
  - Database initialization and account persistence are implemented.
  - Payroll file automation and SSS, HDMF, PhilHealth service stubs are present.
  - Some UI panels are partially implemented; history and statistics features exist but may need completion.
- Future goals:
  - Finish advanced UI module integration and history detail screens.
  - Add export, reporting, and validation features for contribution submission.
  - Harden the account and session security model.
  - Improve error handling, logging, and user feedback.
- Keep generated output directories like `build/` and `dist/` ignored by Git and AI tools.

---

## 2. Architecture

### Overall architecture

GovSync is a PySide6-based desktop application with a layered architecture:

UI
↓
Controller
↓
Service
↓
Repository
↓
Database

### Layer responsibilities

- UI: Builds windows, dialogs, widgets, and event-driven user interface components.
- Controller: Coordinates UI actions and business logic, forwards commands to services.
- Service: Contains processing and business logic. Uses repositories for persistence.
- Repository: Encapsulates SQLite database operations and schema access.
- Database: Local SQLite file persisted under application data directory.

### Folder responsibilities

- `app.py`: Launches the application, shows splash screen, enforces a single-instance lock, and starts the Qt event loop.
- `main_window.py`: Builds the main frameless window, header controls, page stack, and main navigation setup.
- `config.py`: Application constants, directories, database path, UI defaults, and environment override logic.
- `core/`: Application core services and utilities.
  - `application.py`: Builds the dependency container and initializes the DB.
  - `dependency_container.py`: Creates and wires services, repositories, and controllers.
  - `navigation_controller.py`: Coordinates page switching and session-based authentication flow.
  - `page_factory.py`: Creates UI pages and widgets with controller injection.
  - `settings.py`: Loads runtime app settings from `config.py`.
  - `session_manager.py`: Reads and writes persistent active account session state.
  - `logger.py`: Configures application logging.
  - `exceptions.py`: Shared exception types (e.g., `AuthenticationError`).
  - `window_state_manager.py`: Handles window dragging, maximize/minimize, and close events.
- `controllers/`: Application controllers that mediate between UI and services.
  - `auth_controller.py`: Handles login/register/list/delete account operations.
  - `payroll_controller.py`: Delegates payroll file processing.
  - `sss_controller.py`: Delegates SSS TXT generation and file operations.
  - `philhealth_controller.py`: Delegates PhilHealth processing and record management.
  - `hdmf_controller.py`: Delegates HDMF loan separation tasks.
- `services/`: Business logic, processing engines, and data workflows.
  - `auth_service.py`: Password hashing, authentication, and account registration logic.
  - `auth_manager.py`: Higher-level account validation, active account management, superadmin behavior, and repository-backed auth operations.
  - `dashboard_service.py`: Statistic loading, saving, and aggregated totals.
  - `history_service.py`: History record persistence wrapper.
  - `payroll_service.py`: Payroll task execution wrapper.
  - `philhealth_service.py`: PhilHealth engine orchestration and history/statistics recording.
  - `sss_service.py`: SSS generation wrapper and helper exports.
  - `hdmf_service.py`: HDMF loan separation wrapper.
  - `payroll_engine.py`: Core payroll Excel slice generation and formatting logic.
  - `philhealth_engine.py`: PhilHealth data extraction and processing engine.
  - `hdmf_engine.py`: HDMF loan separation engine.
  - `sss_engine.py`: SSS TXT generation engine.
- `repositories/`: SQLite persistence layer.
  - `account_repository.py`: Persists account data and performs CRUD operations.
  - `history_repository.py`: Persists history records and loads them by account.
  - `statistics_repository.py`: Persists module statistics and totals.
- `storage/`: Database connection and schema initialization.
  - `sqlite.py`: SQLite connection helpers, schema creation, and legacy DB migration.
- `models/`: Data models and DTOs.
  - `account.py`: Account dataclass.
  - `history.py`: History record dataclass.
  - `employee.py`: Employee model (exists but usage not fully covered yet).
  - `payroll_result.py`: Payroll result model (exists but usage not fully covered yet).
- `widgets/`: PySide6 widget and panel implementations.
  - `auth_windows.py`: Login and registration UI.
  - `earnings_panel.py`: Earnings automation file panel.
  - `philhealth_panel.py`: PhilHealth module UI.
  - `sss_panel.py`: SSS automation UI.
  - `hdmf_loan_panel.py`: HDMF loan separation UI.
  - `sidebar.py`: Application navigation sidebar.
  - `workspace.py`: Dashboard workspace and stats overview.
  - `right_panel.py`: Context panel and history UI components.
  - `glass_dialog.py`: Modal dialog helper.
  - `glass_panel.py`: Reusable glass-style panel wrapper.
- `shared/`: Shared helpers, constants, and UI utilities.
  - `resources/resources.py`: Asset path utilities and account folder helpers.
  - `ui/icon_utils.py`: Toolbar icon helpers.
  - `ui/ui_icons.py`: Icon constants or helpers.
  - `constants/styles.py`: Shared stylesheet definitions.
- `constants/`: Additional constants and application styling.
- `assets/`: Static assets such as icons and SVG logos.
- `data/`: Legacy or bundled data files.
- `build/` and `dist/`: Build outputs.

### Module communication

- `app.py` creates `GovSyncApplication` and starts the main window.
- `core.application` builds `DependencyContainer` and initializes the database.
- `core.dependency_container` wires `Repositories`, `Services`, and `Controllers`.
- `main_window.py` creates UI pages and passes controllers through `PageFactory`.
- `NavigationController` listens for authentication events and updates page state.
- `AuthController` delegates login/registration to `auth_manager` and `AuthService`.
- UI widgets call controller methods which call services and repositories as needed.
- `services` use `repositories` for SQLite persistence and `engines` for file processing.
- `core.session_manager` persists active account data to JSON in the data directory.

---

## 3. Folder Structure

GovSync/
- app.py: App launch entrypoint.
- app.spec: PyInstaller spec for packaging.
- config.py: Runtime constants and path resolution.
- main_window.py: Main Qt window implementation.
- README.md: Project README.
- CHANGELOG.md, CONTRIBUTING.md: Project maintenance docs.
- RESTRUCTURE_PLAN.md, SYSTEM_ARCHITECTURE.md: Planning docs.
- assets/: Static icons, logos, and UI assets.
- build/: Build artifact outputs.
- constants/: Styling and application-wide constants.
- controllers/: Controllers that mediate UI and service layers.
- core/: Application core orchestration and infrastructure.
- data/: Legacy or external data.
- models/: Typed data classes used by services and repositories.
- repositories/: Database persistence classes.
- services/: Business logic, process orchestration, and engines.
- shared/: Shared utilities, resources, UI helpers.
- storage/: Database initialization and connection helpers.
- widgets/: Main UI widget implementations.
- workers/: Worker thread stubs or concurrency helpers.

Each folder exists to keep concerns separated and to enforce a layered architecture.

---

## 4. File Responsibilities

### Root files
- `app.py`
  - Purpose: application startup, splash, single-instance lock, Qt execution.
  - Inputs: `config` constants, `core.application.GovSyncApplication`.
  - Outputs: running Qt application process.
  - Dependencies: PySide6, `config`, `core.application`, `shared.resources`.
  - Called by: OS when application starts.
  - Calls: `GovSyncApplication`, splash creation, QMessageBox on errors.

- `main_window.py`
  - Purpose: build the main window chrome, navigation header, and page stack.
  - Inputs: dependency container from `GovSyncApplication`.
  - Outputs: `MainWindow` with stacked widgets.
  - Dependencies: PySide6, `core.navigation_controller`, `core.page_factory`, `shared.ui`, `config`.
  - Called by: `GovSyncApplication.create_main_window()`.
  - Calls: `PageFactory`, `NavigationController`, `WindowStateManager`.

- `config.py`
  - Purpose: define global app constants for paths, UI sizes, environment overrides.
  - Inputs: environment variables, OS detection.
  - Outputs: `APP_NAME`, `DATABASE_PATH`, asset and data directories.
  - Dependencies: `pathlib`, `os`.
  - Called by: virtually all modules needing paths or constants.
  - Calls: environment resolution.

### `core/`
- `core/application.py`
  - Purpose: bootstrap container and DB initialization.
  - Inputs: `build_container()`, application settings.
  - Outputs: `GovSyncApplication` instance.
  - Dependencies: `core.dependency_container`, `storage.sqlite`.
  - Called by: `app.py`.
  - Calls: `build_container`, `initialize_database`.

- `core/dependency_container.py`
  - Purpose: central DI container builder.
  - Inputs: settings, repositories, services.
  - Outputs: `DependencyContainer` data object.
  - Dependencies: app settings, logger, repositories, services, controllers.
  - Called by: `core.application.Application`.
  - Calls: constructor functions for each layer.

- `core/navigation_controller.py`
  - Purpose: coordinate UI page changes and session flow.
  - Inputs: page widgets, auth status.
  - Outputs: current page transitions.
  - Dependencies: `core.session_manager`, `services.auth_manager`.
  - Called by: `MainWindow`.
  - Calls: `set_active_account`, `get_active_account`, `get_account`.

- `core/page_factory.py`
  - Purpose: create UI page tree and inject controllers.
  - Inputs: dependency container components.
  - Outputs: login and app page widgets.
  - Dependencies: widget modules, `services.dashboard_service`.
  - Called by: `MainWindow`.
  - Calls: widget constructors, `set_refresh_callback`.

- `core/settings.py`
  - Purpose: wrap app constants into a settings dataclass.
  - Inputs: `config` values.
  - Outputs: `Settings` instance.
  - Dependencies: `dataclasses`, `pathlib`, `config`.
  - Called by: `dependency_container.build_container()`.
  - Calls: none external.

- `core/session_manager.py`
  - Purpose: persistent active account session storage.
  - Inputs: account dictionary.
  - Outputs: JSON file in data directory and normalized account dict.
  - Dependencies: `json`, `pathlib`, `config`.
  - Called by: `services.auth_manager`, `core.navigation_controller`.
  - Calls: file I/O for active account JSON.

- `core/logger.py`
  - Purpose: configure application logging.
  - Inputs: log directory path.
  - Outputs: logger object.
  - Dependencies: missing read details, but likely `logging`.
  - Called by: `dependency_container.build_container()`.

- `core/exceptions.py`
  - Purpose: define exception types for authentication and likely other app errors.
  - Inputs: user and runtime error conditions.
  - Outputs: `AuthenticationError` class.
  - Dependencies: base exception type.
  - Called by: `services.auth_service`, `services.auth_manager`.

- `core/window_state_manager.py`
  - Purpose: custom window dragging, maximize/minimize toggling, and close event handling.
  - Inputs: Qt events.
  - Outputs: window state changes.
  - Dependencies: PySide6 event handling.
  - Called by: `MainWindow` event overrides.

### `controllers/`
- `controllers/auth_controller.py`
  - Purpose: controller interface for auth operations.
  - Inputs: username/password and account fields.
  - Outputs: login role strings, account list/delete results.
  - Dependencies: `services.auth_manager`.
  - Called by: auth UI widgets in `widgets/auth_windows.py`.
  - Calls: `auth_manager.authenticate`, `register_account`, `list_accounts`, `delete_account`.

- `controllers/payroll_controller.py`
  - Purpose: delegate payroll file processing to `PayrollService`.
  - Inputs: file path and optional progress callback.
  - Outputs: payroll processing result tuple.
  - Dependencies: `services.payroll_service`.
  - Called by: `widgets/earnings_panel.py`.

- `controllers/sss_controller.py`
  - Purpose: delegate SSS file generation and load/save operations.
  - Inputs: export arguments and file paths.
  - Outputs: TXT generation path and row counts.
  - Dependencies: `services.sss_service`.
  - Called by: `widgets/sss_panel.py`.

- `controllers/philhealth_controller.py`
  - Purpose: orchestrate PhilHealth processing and persistence.
  - Inputs: account username, record data, process triggers.
  - Outputs: engine process results and history updates.
  - Dependencies: `services.philhealth_service`.
  - Called by: `widgets/philhealth_panel.py`.

- `controllers/hdmf_controller.py`
  - Purpose: delegate HDMF loan separation.
  - Inputs: earnings and monitoring file paths.
  - Outputs: loan separation results.
  - Dependencies: `services.hdmf_service`.
  - Called by: `widgets/hdmf_loan_panel.py`.

### `services/`
- `services/auth_service.py`
  - Purpose: verify passwords, hash registration passwords, and authenticate accounts.
  - Inputs: username/password.
  - Outputs: authenticated `Account` or exceptions.
  - Dependencies: `repositories.account_repository`, `bcrypt` fallback, `hashlib`.
  - Called by: `services.auth_manager`.

- `services/auth_manager.py`
  - Purpose: domain-level auth management, user validation, superadmin handling, and active session storage.
  - Inputs: account credentials and number fields.
  - Outputs: account creation, login role, account list, account deletion.
  - Dependencies: `services.auth_service`, `repositories.account_repository`, `core.session_manager`.
  - Called by: `controllers.auth_controller`, `widgets/auth_windows.py`, `shared.resources`.

- `services/dashboard_service.py`
  - Purpose: compute and persist contribution statistics, totals, and period keys.
  - Inputs: module, employee count, month/year.
  - Outputs: saved stats and aggregated totals.
  - Dependencies: `repositories.statistics_repository`, `repositories.history_repository`, `services.auth_manager`.
  - Called by: `widgets/workspace.py`, `widgets/earnings_panel.py`, `widgets/sss_panel.py`.

- `services/history_service.py`
  - Purpose: wrapper over history repository persistence.
  - Inputs: `HistoryRecord` and account username.
  - Outputs: saved records and history lists.
  - Dependencies: `repositories.history_repository`.
  - Called by: potential controllers or services.

- `services/payroll_service.py`
  - Purpose: wrap payroll engine execution.
  - Inputs: payroll file path.
  - Outputs: processing results.
  - Dependencies: `services.payroll_engine`.
  - Called by: `controllers.payroll_controller`.

- `services/philhealth_service.py`
  - Purpose: run PhilHealth engine, save history, and upsert statistics.
  - Inputs: engine instance, record payloads.
  - Outputs: processed records and updated statistics.
  - Dependencies: `repositories.history_repository`, `repositories.statistics_repository`, `services.philhealth_engine`.
  - Called by: `controllers.philhealth_controller`, `widgets/philhealth_panel.py`.

- `services/sss_service.py`
  - Purpose: SSS TXT workflow and utility exposure for widgets.
  - Inputs: file paths, employer/branch/month/year inputs.
  - Outputs: generated TXT file and counts.
  - Dependencies: `services.sss_engine`.
  - Called by: `controllers/sss_controller`, `widgets/sss_panel.py`.

- `services/hdmf_service.py`
  - Purpose: HDMF loan separation workflow.
  - Inputs: earnings and monitoring file paths.
  - Outputs: updated workbook and loan counts.
  - Dependencies: `services.hdmf_engine`.
  - Called by: `controllers.hdmf_controller`, `widgets/hdmf_loan_panel.py`.

- `services/payroll_engine.py`
  - Purpose: generate payroll tabs and format Excel output for earnings automation.
  - Inputs: Pandas DataFrame from earnings sheet.
  - Outputs: updated workbook sheets and formatting.
  - Dependencies: `pandas`, `openpyxl`, `tkinter` for some helper UI.
  - Called by: `services.payroll_service`.

- `services/philhealth_engine.py`
  - Purpose: implement PhilHealth extraction logic and file processing.
  - Inputs/Outputs: based on `PhicExtractorApp` engine.
  - Dependencies: `openpyxl`, `PySide6` message box substitution.
  - Called by: `services/philhealth_service`.

- `services/hdmf_engine.py`
  - Purpose: separate HDMF loan deductions from earnings workbook.
  - Inputs: earnings and monitoring files.
  - Outputs: updated earnings workbook and loan metrics.
  - Dependencies: `pandas`, `openpyxl`.
  - Called by: `services.hdmf_service`.

- `services/sss_engine.py`
  - Purpose: validate and generate SSS Partial List Data TXT file from worksheet data.
  - Inputs: source workbook, output directory, corrections.
  - Outputs: TXT file and row count.
  - Dependencies: `pandas`, `openpyxl`.
  - Called by: `services/sss_service`.

### `repositories/`
- `repositories/account_repository.py`
  - Purpose: persist accounts and perform account CRUD.
  - Inputs: username, `Account` instances.
  - Outputs: account records or lists.
  - Dependencies: `storage.sqlite`, `models.account`.
  - Called by: `services.auth_service` and `services.auth_manager`.

- `repositories/history_repository.py`
  - Purpose: persist history records and query by account.
  - Inputs: `HistoryRecord` and account usernames.
  - Outputs: record lists and deletion/upsert results.
  - Dependencies: `storage.sqlite`, `models.history`.
  - Called by: `services.history_service`, `services.philhealth_service`.

- `repositories/statistics_repository.py`
  - Purpose: persist contribution totals and query by account/module.
  - Inputs: module statistics.
  - Outputs: totals and account stats dictionaries.
  - Dependencies: `storage.sqlite`.
  - Called by: `services.dashboard_service`, `services.statistics_service`, `services.philhealth_service`.

### `storage/`
- `storage/sqlite.py`
  - Purpose: connect to SQLite and initialize required schema.
  - Inputs: file paths.
  - Outputs: SQLite connection objects and created schema.
  - Dependencies: `sqlite3`, `pathlib`, `shutil`.
  - Called by: application startup and repositories.

### `models/`
- `models/account.py`
  - Purpose: typed account data model.
  - Inputs: username/password and IDs.
  - Outputs: typed account objects.
  - Dependencies: dataclasses.
  - Called by: repositories, services.

- `models/history.py`
  - Purpose: typed history record model.
  - Inputs: history payload fields.
  - Outputs: typed history objects.
  - Dependencies: dataclasses.
  - Called by: repositories, services.

- `models/employee.py`
  - Purpose: employee representation for payroll and contribution data.
  - Inputs/outputs not fully determined; likely used by payroll or export workflows.
  - Dependencies: dataclasses.

- `models/payroll_result.py`
  - Purpose: capture payroll processing results.
  - Inputs/outputs not fully covered in current code.
  - Dependencies: dataclasses.

### `widgets/`
- `widgets/auth_windows.py`
  - Purpose: login and superadmin UI dialogs.
  - Inputs: controller and user interactions.
  - Outputs: auth events and account registration actions.
  - Dependencies: controllers, services, shared resources, PySide6.
  - Called by: `core.page_factory`.

- `widgets/sidebar.py`
  - Purpose: main navigation sidebar and logout.
  - Inputs: navigation items.
  - Outputs: navigation change signals.
  - Dependencies: PySide6, shared resources.
  - Called by: `core.page_factory`.

- `widgets/workspace.py`
  - Purpose: dashboard summary and contribution totals.
  - Inputs: active account and stats.
  - Outputs: refreshed totals UI.
  - Dependencies: `services.dashboard_service`, `widgets.glass_panel`.
  - Called by: `core.page_factory`, `NavigationController`.

- `widgets/earnings_panel.py`
  - Purpose: UI for selecting and processing earnings files.
  - Inputs: user file selections and controller.
  - Outputs: progress UI and history/statistics updates.
  - Dependencies: `controllers.payroll_controller`, `services.dashboard_service`, `auth_manager`, `widgets.glass_dialog`.
  - Called by: `core.page_factory`.

- `widgets/philhealth_panel.py`
  - Purpose: PhilHealth module UI for processing files, viewing history, and displaying record details.
  - Inputs: user file actions, account username, history record payloads, and controller callbacks.
  - Outputs: history card list UI, record detail popups, processing progress feedback, and persisted history records.
  - Dependencies: `controllers.philhealth_controller`, `shared.ui`, `widgets.glass_dialog`, `repositories.history_repository`, `repositories.statistics_repository`, `services.auth_manager`, `constants.styles`.
  - Called by: `core.page_factory`.

- `widgets/sss_panel.py`
  - Purpose: UI for selecting source files, generating SSS TXT output, and persisting user panel state.
  - Inputs: employer ID, branch code, month/year, correction file path, selected payroll source files, controller.
  - Outputs: TXT file generation, progress updates, status notifications, and saved panel state.
  - Dependencies: `controllers.sss_controller`, `services.sss_service`, `services.dashboard_service`, `services.auth_manager`, `widgets.glass_dialog`, `constants.styles`.
  - Called by: `core.page_factory`.

- `widgets/hdmf_loan_panel.py`
  - Purpose: UI for HDMF loan separation.
  - Inputs: earnings and monitoring file paths.
  - Outputs: separated loan results and progress.
  - Dependencies: `controllers.hdmf_controller`, `widgets.glass_dialog`, `constants.styles`.
  - Called by: `core.page_factory`.

- `widgets/right_panel.py`
  - Purpose: right-side workspace context panel with activity log, notes, calendar, history cards, and record preview/detail widgets.
  - Inputs: account username, history records, user note actions, and selected history record.
  - Outputs: activity task display, note management UI, history card interactions, and detail popup views.
  - Dependencies: `widgets.glass_dialog`, `widgets.glass_panel`, `repositories.history_repository`, `repositories.statistics_repository`, `services.auth_manager`, `shared.ui`.

- `widgets/glass_dialog.py`
  - Purpose: custom frameless dialog wrapper.
  - Inputs: title, message, button definitions.
  - Outputs: modal user dialog.
  - Dependencies: PySide6.

- `widgets/glass_panel.py`
  - Purpose: reusable translucent panel with glow effect.
  - Inputs: radius and child content.
  - Outputs: styled widget container.
  - Dependencies: PySide6.

### `shared/`
- `shared/resources/resources.py`
  - Purpose: asset path helpers, account folder creation, shared auth helpers, and normalization utilities.
  - Inputs: filenames, account metadata, and runtime environment.
  - Outputs: safe filesystem paths, normalized account payloads, and data directory utilities.
  - Dependencies: `config`, `core.session_manager`, `repositories.account_repository`, `services.auth_service`.
  - Called by: UI widgets, auth manager, services.

- `shared/ui/icon_utils.py`
  - Purpose: render and assign SVG icons to Qt buttons.
  - Inputs: filenames, colors, sizes.
  - Outputs: `QIcon` objects.
  - Dependencies: PySide6, `shared.helpers.resource_helpers`.
  - Called by: UI components throughout the app.

- `shared/ui/ui_icons.py`
  - Purpose: export UI icon helpers and icon-related public API.
  - Dependencies: `shared.ui.icon_utils`.
  - Called by: other shared UI modules.

- `shared/helpers/resource_helpers.py`
  - Purpose: resolve bundled asset paths with PyInstaller compatibility.
  - Inputs: asset filename.
  - Outputs: absolute filesystem path.
  - Dependencies: `os`, `sys`.

### `constants/`
- `constants/styles.py`
  - Purpose: public alias for shared `AppStyles` constants used by the app.
  - Dependencies: `shared.constants.styles.AppStyles`.

---

## 5. Current Progress

✔ Application skeleton and startup flow
✔ Database initialization and single instance lock
✔ Login / superadmin authentication
✔ Main window and navigation stack
✔ Sidebar and core dashboard workspace
✔ Earnings panel with payroll processing flow
✔ SSS panel scaffolding and TXT generation workflow
✔ HDMF loan panel and loan separation engine
✔ PhilHealth service wrapper and history persistence
✔ Account repository and auth service/password hashing
✔ Employer-name capture, persistence, and account visibility
✔ Account-scoped UI reset and stale-field clearing for SSS, HDMF, and PhilHealth panels
✔ PhilHealth history and deletion scoped to the active account
✔ Phase 1 regression tests added for auth update behavior, payroll import ownership, and SSS banner visibility
✔ Phase 2 bug fixes for auth password updates, payroll duplicate ownership, SSS banner visibility, and PhilHealth session leakage
✔ Phase 3 started with a shared JSON state helper for repeated per-account widget persistence
✔ Phase 3 continued with shared helpers in earnings, SSS, right panel, and auth employer combo wiring

☐ Complete module coverage for history UI
☐ End-to-end PhilHealth workflow verification
☐ UI polish and responsive layout testing
☐ Error handling consistency across all panels
☐ Automated tests and packaging validation
☐ App settings/preferences UI

---

## 6. Current Task

- Current feature being developed: Phase 3 duplication cleanup with low-risk helper extraction, while keeping runtime behavior stable.
- Current bug: The highest-risk regressions have been addressed, but broader duplication and boundary cleanup still remains.
- Current objective: Reduce repeated state-loading/saving code and repeated UI wiring without changing file formats or UI flow.
- Files involved: `shared/helpers/json_state.py`, `widgets/hdmf_loan_panel.py`, `widgets/right_panel.py`, `widgets/earnings_panel.py`, `widgets/sss_panel.py`, `widgets/auth_windows.py`.
- Next action: Continue cautiously with duplication cleanup only where the behavior surface is simple.

---

## 7. TODO List

High
- Add explicit bug tracking and completed issue list to `AI_CONTEXT.md`.
- Validate PhilHealth and SSS full workflow behavior with sample files.
- Add automated tests for auth, repository, and engine components.

Medium
- Finish history details and record management UI.
- Add export/report screens for compliance summaries.
- Harden session persistence and secure account storage.

Low
- Add app settings/preferences UI.
- Polish window sizing, drag behavior, and theme consistency.
- Add more documentation for widget styling standards.

---

## 8. Known Bugs

- Bug description: History UI and record deletion flow may not be fully wired or tested.
  - Possible cause: history persistence exists but some UI components are incomplete.
  - Files involved: `widgets/right_panel.py`, `repositories/history_repository.py`, `services/philhealth_service.py`.
  - Possible fixes: verify signals and record lifecycle, add tests.
  - Current status: unverified.

- Bug description: `HDMF` panel and placeholder page may not match actual module indices.
  - Possible cause: panel order and sidebar index binding are manually mapped.
  - Files involved: `main_window.py`, `widgets/sidebar.py`, `core/page_factory.py`, `core/navigation_controller.py`.
  - Possible fixes: align sidebar list items with stacked widget indices and test navigation.
  - Current status: unverified.

- Bug description: Superadmin credentials are hardcoded and may be insecure.
  - Possible cause: environment variable fallback allows weak default credentials.
  - Files involved: `config.py`, `services/auth_manager.py`.
  - Possible fixes: enforce strong password policy or onboarding flow.
  - Current status: active concern.

---

## 9. Coding Standards

- Naming conventions
  - Use `snake_case` for functions, methods, variables.
  - Use `PascalCase` for classes and dataclasses.
  - Constants are upper-case with underscores.
- Folder rules
  - `controllers/` handle orchestration only.
  - `services/` contain business logic and processing.
  - `repositories/` handle SQLite DB access exclusively.
  - `widgets/` contain Qt UI code only.
- Architecture rules
  - Keep business logic out of UI widgets.
  - Controllers mediate between UI and services.
  - Services call repositories or file processing engines.
  - Models are simple data containers.
- Dependency rules
  - Avoid direct DB access from widgets.
  - Use dependency injection where possible via `DependencyContainer`.
- Import rules
  - Prefer localized imports for optional or heavyweight modules.
  - Keep imports at top of files and avoid wildcard imports.
- Widget creation rules
  - Build reusable widgets in `widgets/` and style with shared CSS where possible.
  - Use signals/slots for UI communication.
- Error handling
  - Catch and report exceptions in `app.py` startup.
  - Prefer user-friendly error dialogs for file workflows.
- Database access rules
  - Use `storage.sqlite.connect()` with `row_factory`.
  - Initialize DB schema on startup.
- Service rules
  - Keep services stateless when possible.
  - Allow optional callbacks for progress and message boxes.

---

## 10. UI Standards

- Color palette
  - Dark theme with teal/green highlights (#14b8c8, #34d399), blue accents (#3b82f6), and gray text.
- Fonts
  - `Segoe UI` is the primary font family.
  - Use bold text for headings and UI labels.
- Spacing
  - Consistent padding around panels and dialogs.
  - Use 10-20px vertical spacing between sections.
- Margins
  - Main layout margins are typically 10-16px.
- Button styles
  - Primary buttons use gradient backgrounds and white text.
  - Secondary buttons use darker backgrounds with subtle borders.
- Card styles
  - Glass panels use translucent dark backgrounds with rounded corners.
- Animation rules
  - No explicit animation system visible; use simple Qt transitions where needed.
- Icons
  - Use SVG icon helpers with theme colors.
- Consistency rules
  - Keep shared styles in `constants/styles.py` and `widgets/glass_panel.py`.

---

## 11. Database

- Tables
  - `accounts`: stores user credentials, account numbers, and timestamps.
  - `history_records`: stores historical module processing results.
  - `statistics`: stores account/module totals by period.
- Relationships
  - `history_records.account_username` references account identity by username.
  - `statistics.account_username` references account identity by username.
- Repositories
  - `AccountRepository` for account CRUD.
  - `HistoryRepository` for history CRUD.
  - `StatisticsRepository` for totals and replacement.
- Models
  - `Account` maps account fields and metadata.
  - `HistoryRecord` maps history payloads and metadata.
- Queries
  - `SELECT` by username, module, and period key.
- Transactions
  - repository methods commit after inserts/updates/deletes.

---

## 12. Design Decisions

### Decision: Use PySide6 for UI
- Reason: Desktop native app with Qt widgets and custom styling.
- Advantages: cross-platform GUI with modern widgets.
- Disadvantages: larger dependency and packaging complexity.
- Alternative considered: web-based UI or other GUI frameworks.
- Date: 2026-06-27

### Decision: Use SQLite local DB
- Reason: simple embedded storage for accounts and history.
- Advantages: no external DB dependency.
- Disadvantages: concurrency and scaling limitations.
- Alternative considered: file-based JSON storage or server-backed DB.
- Date: 2026-06-27

### Decision: Separate controllers from services
- Reason: preserve clean separation of UI orchestration and business logic.
- Advantages: easier testing and maintainability.
- Disadvantages: extra layer of indirection.
- Alternative considered: direct service wiring into widgets.
- Date: 2026-06-27

---

## 13. Session Log

### Session 1
Completed:
- Created `AI_CONTEXT.md` with project overview, architecture, file responsibilities, progress, and handoff guidance.
- Mapped root app flow, dependency container, service layer, repository layer, and widget layer.
Next:
- Validate and update context after every code change.
- Add explicit bug tickets and task tracking.

### Session 2
Completed:
- Documented employer-name support in account creation, persistence, and account listings.
- Recorded account-scoped UI resets for SSS, HDMF, and PhilHealth panels.
- Documented PhilHealth history scoping and account-safe deletion behavior.
Next:
- Keep markdown files current as further fixes land.
- Preserve the existing UI while improving state handling and persistence.

### Session 3
Completed:
- Added phase 1 regression tests covering auth account updates, payroll import ownership, and SSS banner visibility.
- Marked known logic bugs as xfailed tests so refactor work can proceed with explicit guardrails.
Next:
- Fix the xfailed regressions during the next logic-focused phase.
- Keep the docs synchronized with any behavior changes.

### Session 4
Completed:
- Fixed account update password handling so password changes are rehashed before persistence.
- Unified payroll duplicate lookup ownership with the same identifier stored in the import plan.
- Restored the SSS account banner visibility when a linked SSS number exists.
- Removed the PhilHealth panel's redundant session write and set selected history tracking when opening records.
Next:
- Confirm the updated regression tests and continue with broader refactor cleanup.
- Keep the docs synchronized with any behavior changes.

### Session 5
Completed:
- Added a shared JSON state helper for repeated widget persistence.
- Swapped HDMF loan panel and right panel state load/save logic to the shared helper without changing file layout.
Next:
- Expand duplication cleanup only when the code path is similarly low-risk.
- Avoid changing user-visible behavior while consolidating helpers.

### Session 6
Completed:
- Reused the shared JSON helper in the earnings panel and SSS panel.
- Extracted shared employer combo wiring in the auth UI to reduce duplicate setup code.
- Consolidated repeated auth account registration branching into one helper.
- Removed an unused import from the right panel cleanup.
Next:
- Keep refactoring cautious and behavior-preserving.
- Only move into riskier structural cleanup after the current helpers settle.

### Session 7
Completed:
- Added a shared account username resolver for panels that only need normalized account state switching.
- Reused the resolver in the earnings panel, HDMF loan panel, right panel, and PhilHealth panel.
Next:
- Keep phase 4 limited to similarly low-risk helper extraction.
- Avoid broader structural edits unless we have a clearly isolated duplicate pattern.

### Session 8
Completed:
- Reused the shared account username resolver for panel startup defaults in earnings, HDMF loan, and SSS.
Next:
- Continue with only isolated, behavior-preserving duplicate removal.
- Stop before touching shared flows that also carry panel-specific state.

### Session 9
Completed:
- Added a shared account-state path helper to keep per-account panel JSON path construction consistent.
- Reused that helper in earnings, HDMF loan, right panel, and SSS state persistence.
Next:
- Keep future refactors similarly small and reversible.
- Avoid broad orchestration changes unless they are separately justified.

### Session 10
Completed:
- Made the employee records panel load data off the UI thread with a queued refresh path.
- Reset employee list pagination when filters change so narrowing results does not land on empty pages.
- Fixed employee detail history lookup to prefer the selected row's employer context.
- Restricted the auth shell drag behavior to the header area only.
Next:
- Keep the remaining UI fixes similarly conservative.
- Check other fixed-size layouts for clipping only after the current changes settle.

### Session 11
Completed:
- Fixed the authenticated session write so the active account updates immediately after login.
- Restored the PhilHealth popup minimum width after testing the safer session-state fix.
Next:
- Continue looking for isolated UI state bugs before touching broad layout structure.
- Avoid shrinking table dialogs below the space needed for their visible columns.

### Session 12
Completed:
- Rebuilt the employee records paginator with clean text and compact-mode support.
- Added responsive footer sizing in the employee records panel so the table and paginator compress together.
- Made the right panel calendar, activity log, and notes section shrink dynamically when the window height is tight.
Next:
- Keep testing the smallest window size against clipped content before widening the scope again.
- Only touch other fixed-size widgets if they show the same kind of overflow pressure.

### Session 13
Completed:
- Relaxed the right panel notes inner container minimum height in compact mode so the bottom notes area can actually collapse instead of clipping offscreen.
- Kept the notes stack expandable again when the panel has room, so the normal layout still looks the same.
Next:
- Watch for any other nested scroll areas that retain hidden minimum heights during resize.
- Avoid reintroducing fixed minimums inside panels that already have runtime resize logic.

### Session 14
Completed:
- Added compact-mode resizing to the employee records header so the stats and filters use less vertical space when the window is short.
- Tightened the employee records footer and table row heights in compact mode so the pagination bar can stay visible.
- Removed the right panel's layout minimum-size constraint and made its calendar, activity log, and notes shrink from the actual window height.
Next:
- Verify the smallest window size again and keep trimming only the remaining hard-coded floors.
- Avoid reintroducing layout constraints that force hidden spacer space below the visible content.

---

## 14. AI Handoff

Current architecture:
- PySide6 UI front-end.
- `core/` orchestrates DI and navigation.
- `controllers/` expose operations to widgets.
- `services/` contain domain logic and file processing.
- `repositories/` persist data to SQLite.
- `storage/` initializes database.
- `models/` define typed record containers.

Current files:
- `app.py`, `main_window.py`, `config.py`
- `core/`: application bootstrap, DI, navigation, session handling
- `controllers/`: auth, payroll, SSS, PhilHealth, HDMF delegation
- `services/`: payroll, auth, dashboard, history, PhilHealth, SSS, HDMF
- `repositories/`: accounts, history, statistics
- `widgets/`: UI panels, dialogs, navigation, dashboards
- `shared/`: icons, resources, helpers, styles

Current unfinished code:
- History UI and record lifecycle likely incomplete.
- PhilHealth page and data extraction need end-to-end verification.
- State persistence and UI save/load across account changes require validation.

Current bugs / risks:
- Superadmin is hardcoded and not securely enforced.
- Sidebar navigation may be brittle if index mapping changes.
- Unverified history and statistics integration.
- Packaging with PySide6 and external engines may require dependency validation.

What should be done next:
- Keep `AI_CONTEXT.md` current with code changes.
- Add tests for key services and session flows.
- Confirm UI event wiring for all panels.
- Improve security and configuration for admin credentials.
- Add explicit issue tracking if any bug is reproduced.

Dependencies:
- Python 3.x
- PySide6
- pandas
- openpyxl
- bcrypt (optional)

Assumptions:
- The application is Windows-focused but likely cross-platform.
- `assets/` contains icons used by UI helpers.
- Some widget files may include additional details not fully covered in this initial pass.

---

## 15. Refactoring History

- Initial architecture is layered around UI → Controller → Service → Repository.
- No major refactor history present yet.
- Note: if architecture changes, record old/new layers and reason here.

---

## 16. Important Commands

- `python app.py`: start the application.
- `pytest`: run tests if added.
- `pyinstaller app.spec`: build distributable package.
- `git status`, `git diff`, `git commit -m "..."`.

---

## 17. Project Rules

- Keep business logic outside the UI.
- Controllers coordinate between UI and services.
- Services contain business logic.
- Repositories handle database operations only.
- Models represent data only.
- Widgets never directly access the database.
- Avoid duplicated code.
- Prefer reusable components.
- Keep modules loosely coupled.

---

## 18. AI Instructions

Whenever code is modified:
1. Read `AI_CONTEXT.md` first.
2. Update it after making changes.
3. Record what changed.
4. Record why it changed.
5. Update Current Progress.
6. Update Current Task.
7. Update Session Log.
8. Update TODO list.
9. Update AI Handoff.
10. Never leave the documentation outdated.

If information is missing, infer it from the project structure and code, but clearly mark inferred information as assumptions.
