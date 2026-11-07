# API reference
Interactive docs: `http://localhost:8000/docs` (Swagger) and `/redoc`. All `/api/*` endpoints except
login require `Authorization: Bearer <token>`. List endpoints return `{ "total": n, "items": [...] }`
and accept `skip` (>= 0) and `limit` (1-100).

| Method | Path | Roles | Description |
|---|---|---|---|
| GET | `/health` | public | Liveness check |
| POST | `/api/auth/login` | public | Form login (`username`, `password`) -> JWT |
| GET | `/api/auth/me` | any | Current user |
| POST | `/api/auth/users` | admin | Create user |
| GET | `/api/taxpayers` | any | List/search (`q`) active taxpayers |
| POST | `/api/taxpayers` | admin, officer | Create taxpayer (409 on duplicate NPWPD) |
| GET | `/api/taxpayers/{id}` | any | Get taxpayer |
| PUT | `/api/taxpayers/{id}` | admin, officer | Update name/address/category |
| DELETE | `/api/taxpayers/{id}` | admin | Soft delete (204) |
| GET | `/api/transactions` | any | Filters: `taxpayer_id`, `date_from`, `date_to`, `flagged_only` |
| POST | `/api/transactions` | admin, officer | Create; computes tax, may flag |
| POST | `/api/transactions/{id}/clear-flag` | admin, auditor | Clear a flag (409 if not flagged) |
| GET | `/api/dashboard/summary` | any | Totals, per-category, last 6 months |
| GET | `/api/audit` | admin, auditor | Audit trail, newest first |

## Business rules
- Tax rates: hotel 10%, restoran 10%, hiburan 15%, parkir 10%; rounded half up to whole rupiah.
- Flag `above_threshold` when amount >= `ANOMALY_THRESHOLD` (default Rp 50,000,000).
- Flag `spike_vs_average` when the taxpayer has >= 5 prior transactions and the amount is > 3x
  the average of the last 20.
- `trx_date` cannot be more than 1 day in the future (time-zone tolerance); `amount` must be 1..10,000,000,000.

## Error format
`{"detail": "message"}` or, for validation errors (422), a list of field errors.
Codes used: 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict, 422 validation.
