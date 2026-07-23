# Architecture

GovSync follows a layered architecture that keeps UI concerns separate from business logic and persistence.

## Architectural shape

```text
PySide6 widgets
  -> controllers
  -> services
  -> repositories
  -> SQLite
```

## Responsibilities

- Widgets: build UI, display data, emit events.
- Controllers: translate UI actions into service calls.
- Services: contain business rules, validation, and workflows.
- Repositories: encapsulate database access and CRUD operations.
- Storage: manage SQLite connections and schema initialization.

## Key design principles

- Keep each layer focused on one responsibility.
- Prefer dependency injection over hidden global state.
- Keep widgets thin and avoid direct persistence access.
- Keep services free from UI construction.

## Main structure

- [core/](../core/) manages app bootstrapping, navigation, settings, and session state.
- [controllers/](../controllers/) mediate between widgets and services.
- [services/](../services/) implement payroll and compliance workflows.
- [repositories/](../repositories/) isolate persistence implementation.
- [widgets/](../widgets/) contain feature panels, dialogs, and layout components.

## Dependency rules

Allowed:

- Widget -> Controller
- Controller -> Service
- Service -> Repository
- Repository -> Database

Forbidden:

- Widget -> Repository
- Widget -> Database
- Service -> Widget
- Repository -> Widget
