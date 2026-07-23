# GovSync System Architecture

**Version:** 2.0\
**Architecture Style:** Feature-First (Vertical Slice) + Layered
Architecture\
**Framework:** PySide6\
**Database:** SQLite\
**Language:** Python 3

## Core Domain Model

- Accounts are authenticated users and may be linked to a normalized employer record through `employer_id`.
- Employers are canonical records for company-level metadata such as name, address, and contribution numbers.
- Account-level employer data remains available as compatibility fields while the app moves toward employer-first persistence.

------------------------------------------------------------------------

# Overview

GovSync is a desktop application for processing and managing Philippine
government employee benefit data while maintaining a clean separation
between the UI, business logic, and persistence layers.

------------------------------------------------------------------------

# High-Level Architecture

``` text
User
 │
 ▼
PySide6 Widgets (UI)
 │
 ▼
Controllers
 │
 ▼
Services
 │
 ▼
Repositories
 │
 ▼
SQLite Database
```

The UI never communicates directly with repositories or the database.

Authentication and registration flow through the controller/service/repository layers, where employer resolution happens before the account is persisted.

------------------------------------------------------------------------

# Project Structure

``` text
app/
├── core/
├── shared/
│   ├── constants/
│   ├── database/
│   ├── helpers/
│   ├── infrastructure/
│   ├── resources/
│   └── ui/
├── features/
│   ├── auth/
│   ├── payroll/
│   ├── philhealth/
│   ├── sss/
│   ├── hdmf/
│   └── dashboard/
└── main.py
```

------------------------------------------------------------------------

# Standard Feature Layout

``` text
feature/
├── controllers/
├── services/
├── repositories/
├── models/
├── widgets/
├── validators/
└── tests/
```

------------------------------------------------------------------------

# Layer Responsibilities

## Widgets

-   Display data
-   Receive user input
-   Call controllers

Never: - Execute SQL - Contain business logic - Access repositories
directly

## Controllers

-   Receive requests from widgets
-   Coordinate services
-   Return results

Controllers should remain thin.

## Services

-   Business rules
-   Validation
-   Workflow orchestration
-   Processing logic

## Repositories

-   CRUD operations
-   Database queries
-   Persistence

## Models

-   Dataclasses
-   DTOs
-   Domain entities

## Shared

Reusable utilities that are not feature-specific.

Business logic should never live here.

------------------------------------------------------------------------

# Dependency Rules

Allowed:

``` text
Widget
 ↓
Controller
 ↓
Service
 ↓
Repository
 ↓
Database
```

Forbidden:

-   Widget → Repository
-   Widget → Database
-   Service → Widget
-   Repository → Widget

------------------------------------------------------------------------

# Dependency Injection

Dependencies are created by the application's dependency container.

-   Widgets receive Controllers
-   Controllers receive Services
-   Services receive Repositories
-   Repositories receive Database connections

------------------------------------------------------------------------

# Example Flow

``` text
PayrollWidget
      ↓
PayrollController
      ↓
PayrollService
      ↓
PayrollRepository
      ↓
SQLite
```

------------------------------------------------------------------------

# MainWindow

MainWindow should only: - Assemble the application - Initialize pages -
Manage navigation

It should not contain business logic.

------------------------------------------------------------------------

# Coding Standards

-   SOLID
-   DRY
-   KISS
-   Dependency Injection
-   Type Hints
-   Composition over Inheritance

------------------------------------------------------------------------

# Goals

-   Easy to maintain
-   Easy to extend
-   Easy to test
-   Low coupling
-   High cohesion
