# Test plan

## Objectives
Protect the business rules (tax, anomaly flags), security (authN/authZ), data integrity (audit,
soft delete) and the user-facing flows, with fast feedback on every commit.

## Test pyramid
| Level | Where | Tool | Count | Purpose |
|---|---|---|---|---|
| Unit | `backend/tests/unit` | pytest | 23 | Pure logic: tax, anomaly, hashing, JWT, config guard |
| API / integration | `backend/tests/api` | pytest + TestClient + in-memory SQLite | 38 | Endpoints, validation, RBAC, DB behaviour |
| Regression | `backend/tests/regression` | pytest (`-m regression`) | 10 | Baseline of critical behaviours (REG-001..010) |
| Browser E2E | `frontend/e2e` | Playwright (Chromium) | 8 tests | Real UI + real API: login, RBAC, responsive layout, officer-to-auditor workflow |
| E2E smoke | `scripts/smoke_test.py` | httpx against a live server | 11 checks | Deployed stack sanity; CI runs it on PostgreSQL |
| Manual | `docs/MANUAL_TEST_CASES.md` | human | 24 cases | UI flows, usability, responsive layout |
| Static analysis | CI | ruff, next lint | - | Style, bugs, import order |

## How to run
See README "Testing". Markers: `unit`, `api`, `regression` (registered in `pyproject.toml`, `--strict-markers`).

## Quality gates (CI)
1. `ruff check` and `ruff format --check` clean.
2. All tests green; coverage >= 90% (currently ~98%).
3. Playwright E2E suite passes (CI job `e2e`, report uploaded on failure).
4. Alembic migrations apply to a real PostgreSQL; seed and smoke test pass.
5. Frontend `npm run lint` and `npm run build` pass.

## Regression policy
- Every fixed defect gets a `REG-xxx` test written **before** the fix is merged.
- The regression suite runs on every pull request and before each release.
- Do not delete a REG test without recording why in CHANGELOG.

| ID | Behaviour protected | Test |
|---|---|---|
| REG-001 | Tax rounds half up using integers (1,005 -> 101) | `test_reg001_tax_rounding_is_half_up_integer` |
| REG-002 | Future-dated transactions are rejected (beyond 1-day tolerance) | `test_reg002_future_dated_transaction_rejected` |
| REG-003 | Deactivated taxpayers cannot receive transactions | `test_reg003_deleted_taxpayer_cannot_receive_transactions` |
| REG-004 | Duplicate NPWPD returns 409, not 500 | `test_reg004_duplicate_npwpd_is_409_not_500` |
| REG-005 | Auditor is read-only for transactions | `test_reg005_auditor_is_read_only_for_transactions` |
| REG-006 | A flag cannot be cleared twice | `test_reg006_flag_cannot_be_cleared_twice` |
| REG-007 | Page size is capped (limit <= 100) | `test_reg007_page_size_is_capped` |
| REG-008 | Deactivated user's token stops working | `test_reg008_deactivated_user_token_is_rejected` |
| REG-009 | Password hash never exposed in responses | `test_reg009_password_hash_never_exposed` |
| REG-010 | Clearing a flag leaves an audit record | `test_reg010_clearing_a_flag_leaves_audit_record` |

## Test data
API tests build their own data through fixtures (`auth`, `make_taxpayer`, `make_trx`) in an isolated
in-memory database per test: no shared state, order-independent. Manual and E2E tests use the seed data (E2E in its own `backend/e2e.db`, with unique names per run).

## Known gaps / next steps
- E2E covers the main journeys only; add visual regression and cross-browser (Firefox/WebKit) projects.
- No load/performance tests (add k6 or Locust against `/api/transactions`).
- No frontend unit tests (add Vitest + Testing Library for `Shell` and `api.js`).
