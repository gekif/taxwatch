# TaxWatch - Regional Tax Transaction Monitoring

A full-stack portfolio project modelled on real-world regional revenue-office systems
(e-tax / tapping-box monitoring). It ingests taxable transactions from business owners
(hotels, restaurants, entertainment venues, parking), calculates tax automatically, flags
suspicious transactions for review, and keeps a complete audit trail.

**Stack:** FastAPI - PostgreSQL (SQLAlchemy 2, Alembic) - Next.js 14 (React) - Docker - GitHub Actions

## Features
- JWT authentication with role-based access control: **admin**, **officer**, **auditor**
- Taxpayer management (validation, unique NPWPD, soft delete)
- Transactions with integer-only tax calculation (half-up rounding) and anomaly detection
  (`above_threshold`, `spike_vs_average`)
- Auditor workflow: review and clear flagged transactions
- Dashboard: totals, monthly revenue chart, per-category breakdown
- Immutable audit trail of every change (who, what, when)

## Repository layout
```
backend/    FastAPI app, Alembic migrations, tests (unit / api / regression)
frontend/   Next.js app (App Router)
docs/       Architecture, UML, API, test plan, manual test cases, best practices
scripts/    End-to-end smoke test against a running API
```

## Quick start (local, PyCharm friendly)
Prerequisites: Python 3.12+, Node.js 20+, and optionally PostgreSQL 16 (SQLite works out of the box).

```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows   |   source .venv/bin/activate   (macOS/Linux)
python -m pip install -r requirements-dev.txt
copy ..\.env.example .env         # Windows   |   cp ../.env.example .env
python -m alembic upgrade head    # create schema
python -m app.seed                # demo users + 180 days of data
python -m uvicorn app.main:app --reload
# API docs: http://localhost:8000/docs

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev                       # http://localhost:3000
```
Demo logins (password `Demo#12345`): `admin`, `officer`, `auditor`. **Demo data only.**

### Using PostgreSQL (e.g. via DataGrip)
```bash
docker run --name taxwatch-db -e POSTGRES_USER=taxwatch -e POSTGRES_PASSWORD=taxwatch \
  -e POSTGRES_DB=taxwatch -p 5432:5432 -d postgres:16-alpine
```
Set `DATABASE_URL=postgresql+psycopg2://taxwatch:taxwatch@localhost:5432/taxwatch` in `backend/.env`,
re-run the Alembic and seed commands, then connect DataGrip to `localhost:5432`.
The same works with a Supabase Postgres connection string (use the session pooler).

### PyCharm run configuration
Run -> Edit Configurations -> Python: **Module name** `uvicorn`, **Parameters** `app.main:app --reload`,
**Working directory** `backend`. For tests add a **pytest** configuration with working directory `backend`.

### Docker (full stack)
```bash
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))") docker compose up --build
```
(Docker files were not executed in the authoring environment; see docs/BEST_PRACTICES.md.)

## Testing
```bash
cd backend
python -m pytest                          # everything (71 tests)
python -m pytest -m unit                  # fast unit tests
python -m pytest -m api                   # API / integration tests
python -m pytest -m regression            # regression suite (REG-001..010)
python -m pytest --cov --cov-report=html  # coverage report in htmlcov/

# End-to-end smoke test against a running API (after migrate + seed)
cd ..
python -m pip install httpx
python -m scripts.smoke_test

# Browser E2E tests (Playwright) - drive the real UI against the real API
cd frontend
npm install
npm run e2e:install        # first time only: downloads Chromium
npm run e2e                # auto-starts backend (SQLite backend/e2e.db) and frontend
npm run e2e:ui             # interactive mode  |  npm run e2e:report  -> HTML report
# Windows without an activated venv:  set E2E_PYTHON=..\backend\.venv\Scripts\python.exe
# Reset E2E data: delete backend/e2e.db

# Lint / format
cd backend
python -m ruff check . && python -m ruff format --check .
```
Manual test cases: [docs/MANUAL_TEST_CASES.md](docs/MANUAL_TEST_CASES.md). Strategy: [docs/TEST_PLAN.md](docs/TEST_PLAN.md).

## Documentation
| Document | Content |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, design decisions, trade-offs, roadmap |
| [docs/UML.md](docs/UML.md) | Use case, class, ER, sequence and deployment diagrams (Mermaid) |
| [docs/API.md](docs/API.md) | Endpoint reference and role matrix |
| [docs/TEST_PLAN.md](docs/TEST_PLAN.md) | Test pyramid, regression policy, coverage gate |
| [docs/MANUAL_TEST_CASES.md](docs/MANUAL_TEST_CASES.md) | 24 step-by-step manual test cases |
| [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) | Engineering practices applied + checklist |
| [SECURITY.md](SECURITY.md) | Security model and known limitations |

## License
MIT
