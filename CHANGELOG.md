# Changelog
All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and SemVer.

## [1.1.0] - 2026-11-03
### Added
- Playwright E2E suite (`frontend/e2e`, 8 tests) with auto-started backend + frontend, CI job `e2e`.
### Fixed
- Transaction date validation rejected "today" for users ahead of the server time zone; now tolerates
  1 day, and the UI uses the local calendar date. Covered by a new API test.

## [1.0.0] - 2026-11-03
### Added
- FastAPI backend: JWT auth with roles (admin / officer / auditor), taxpayers CRUD (soft delete),
  transactions with automatic tax calculation and anomaly flagging, dashboard summary, audit trail.
- PostgreSQL schema managed by Alembic migrations; demo seed data.
- Next.js frontend: login, dashboard with chart, taxpayers, transactions, audit trail.
- Test suites: unit, API/integration, regression (REG-001..010), E2E smoke script, manual test cases.
- Docs: architecture, UML (Mermaid), API reference, test plan, best practices, security notes.
- Docker Compose, GitHub Actions CI (lint, tests with coverage gate, PostgreSQL migration + smoke).
