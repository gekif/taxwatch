# Architecture

## Context
Regional revenue offices receive transaction data from taxable businesses (hotels, restaurants,
entertainment, parking). TaxWatch lets officers register taxpayers and transactions, computes the
tax, flags anomalies, and lets auditors review them, with every action recorded.

## Layers (backend)
| Layer | Location | Responsibility |
|---|---|---|
| HTTP / routing | `app/routers/*` | Request parsing, authorization (role dependencies), status codes |
| Schemas | `app/schemas.py` | Validation and response contracts (Pydantic v2) |
| Business rules | `app/services.py` | Pure functions: `calculate_tax`, `detect_anomaly`; audit helper |
| Persistence | `app/models.py`, `app/database.py` | SQLAlchemy 2 models, session management |
| Cross-cutting | `app/security.py`, `app/deps.py`, `app/config.py` | Hashing/JWT, auth dependencies, settings |
| Migrations | `alembic/` | Versioned schema changes (source of truth for the schema) |

Frontend: Next.js App Router. `lib/api.js` centralises fetch, auth header, and error handling;
`components/Shell.js` guards routes and renders role-aware navigation.

## Key design decisions
1. **Integer rupiah** (`BigInteger`) and integer arithmetic for tax: no floating-point money errors.
2. **Pure business rules** separated from I/O so they are unit-tested without a database.
3. **Soft delete for taxpayers**: historical transactions must stay valid for audits.
4. **Audit log written in the same DB transaction** as the change (atomic, no orphan records);
   `actor` is denormalised so history survives user changes.
5. **Alembic owns the schema**; tests use `create_all` on in-memory SQLite for speed, and CI also
   runs migrations + smoke test on real PostgreSQL to catch dialect differences.
6. **Role checks as dependencies** (`require_roles`) so authorization is declarative and testable.
7. **Pagination everywhere** with a capped page size (`limit <= 100`) to protect the database.

## Trade-offs and future work
- Monthly aggregation uses SQL `extract`; for large volumes use materialised views or a rollup table.
- Anomaly rules are simple heuristics; replace with statistical/ML scoring behind the same interface.
- Real tapping-box ingestion would add an authenticated device endpoint, idempotency keys, and a queue.
- Add refresh tokens, rate limiting, structured JSON logging, metrics (Prometheus), and tracing.
- Frontend: TypeScript, component tests (Vitest + Testing Library), Playwright E2E.
