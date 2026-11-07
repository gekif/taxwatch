# Engineering best practices applied

## Code and design
- [x] Layered backend (routers / schemas / services / models); business rules are pure functions
- [x] Type hints and Pydantic validation at the boundary; explicit response models (no leaking fields)
- [x] Money as integers; deterministic rounding rule with tests
- [x] Consistent error contract and HTTP status codes (401/403/404/409/422)
- [x] Pagination with capped page size; eager loading (`selectinload`) to avoid N+1 queries
- [x] Database indexes on lookup/filter columns; foreign keys; unique constraints
- [x] Soft delete and audit trail for traceability

## Security
- [x] Salted PBKDF2 password hashing, JWT with expiry, server-side RBAC
- [x] Secrets only via environment variables; `.env` git-ignored; `.env.example` provided
- [x] Production fails fast on weak `SECRET_KEY`; CORS limited to configured origins
- [x] Container runs as non-root user
- [ ] Open items listed in SECURITY.md (rate limiting, httpOnly cookies, MFA)

## Testing and quality
- [x] Test pyramid (unit, API, regression, Playwright E2E, smoke, manual); coverage gate in CI (>= 90%)
- [x] Isolated tests (fresh in-memory DB per test), fast feedback (~2 s for 71 tests)
- [x] Linting and formatting (ruff, ESLint), pre-commit hooks

## Delivery and operations
- [x] Alembic migrations; one command to migrate and seed
- [x] CI: lint, test, migrate on real PostgreSQL, smoke test, frontend build
- [x] Dockerfiles and Docker Compose with DB health check
- [x] Health endpoint, structured log format, CHANGELOG (SemVer), MIT license

## Verification status (be transparent)
Verified in the authoring environment: backend tests (71 passed, ~98% coverage), ruff, Alembic
migration + seed on SQLite, live API smoke test, frontend lint and production build, and the 8 Playwright E2E tests (run twice, both green; Chromium was supplied via `PW_CHROMIUM_PATH` because the standard browser download was blocked there).
**Not executed there:** Docker/Compose files, the GitHub Actions workflow (including the new `e2e` job), PostgreSQL run (the SQL is
dialect-neutral and CI exercises PostgreSQL), manual test cases, and the Mermaid rendering.

## Git workflow suggestion
Trunk-based with short-lived branches, Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`),
pull requests that must pass CI, and a REG test added with every bug fix.
