# Features

GovSync is organized around a small set of core business modules.

## Core modules

- Dashboard — workspace overview and summary state, implemented around the main window and related widgets
- Payroll — payroll automation and processing workflows in [services/](../services/) and [controllers/](../controllers/)
- SSS — SSS contribution file generation and related panels in [widgets/](../widgets/)
- PhilHealth — PhilHealth processing and record handling in [services/](../services/) and [widgets/](../widgets/)
- HDMF — HDMF loan and contribution workflows in [services/](../services/) and [widgets/](../widgets/)
- Settings and account management — account switching, employer handling, and session context in [core/](../core/) and [controllers/](../controllers/)

## Feature notes

Each feature should remain focused on its business workflow while relying on shared infrastructure for navigation, persistence, and UI composition.
