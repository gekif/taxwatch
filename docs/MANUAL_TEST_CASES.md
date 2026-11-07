# Manual test cases
**Preconditions:** backend and frontend running, database migrated and seeded (`python -m app.seed`).
Accounts (password `Demo#12345`): `admin`, `officer`, `auditor`. Record result as Pass/Fail with date and tester.

| ID | Title | Steps | Expected result |
|---|---|---|---|
| MT-01 | Login success | Open `/`, sign in as `officer` | Redirected to Dashboard; header shows "Field Officer (officer)" |
| MT-02 | Login wrong password | Sign in as `officer` with a wrong password | Red error "Incorrect username or password"; stays on login |
| MT-03 | Route guard | In a new private window open `/dashboard` directly | Redirected to login page |
| MT-04 | Role-based navigation | Log in as `auditor`, then as `officer` | Auditor sees "Audit trail" link; officer does not |
| MT-05 | Dashboard | Log in, open Dashboard | 4 stat cards, monthly bar chart (up to 6 months), category table with 4 rows |
| MT-06 | Create taxpayer | As `officer`, Taxpayers: NPWPD `HTL000099`, name "Test Inn", category hotel, Add | Row appears in list; count increases by 1 |
| MT-07 | Duplicate NPWPD | Repeat MT-06 with the same NPWPD | Error "NPWPD already registered"; no new row |
| MT-08 | Invalid NPWPD | Enter NPWPD `ab` and submit | Validation error is shown; no row created |
| MT-09 | Search taxpayers | Type "hotel" in search box | List filters to matching names/NPWPDs |
| MT-10 | Deactivate taxpayer | As `admin`, click Deactivate on "Test Inn" and confirm | Row disappears; count decreases |
| MT-11 | Deactivate hidden for officer | As `officer`, view Taxpayers | No Deactivate buttons |
| MT-12 | Read-only auditor | As `auditor`, view Taxpayers and Transactions | No "Add taxpayer" or "Record transaction" forms |
| MT-13 | Record normal transaction | As `officer`, Transactions: pick a hotel, amount 1,000,000, today | New row at top; tax Rp 100.000; no flag badge |
| MT-14 | Tax rate for entertainment | Record 2,000,000 for the hiburan taxpayer | Tax is Rp 300.000 (15%) |
| MT-15 | Flag above threshold | Record 60,000,000 for any taxpayer | Row shows red badge `above_threshold` |
| MT-16 | Future date blocked | Pick a date after today in the UI (picker `max`); via Swagger `POST /api/transactions` use a date 2+ days ahead | UI prevents it; API returns 422 (1 day ahead is tolerated for time zones) |
| MT-17 | Flagged filter | Tick "Show flagged only" | Only flagged rows shown; counter updates |
| MT-18 | Pagination | Without filters, click Next then Previous | Next page loads; Previous disabled on first page; range text correct |
| MT-19 | Clear flag | As `auditor`, click Clear flag on a flagged row | Badge disappears; dashboard "Flagged" count decreases by 1 |
| MT-20 | Clear flag hidden for officer | As `officer`, view a flagged row | No "Clear flag" button |
| MT-21 | Audit trail | As `auditor`, open Audit trail after MT-06..MT-19 | Entries for create taxpayer, create transaction, clear_flag with correct actor |
| MT-22 | Logout / session | Click Log out, then press Back | Login page shown; protected pages redirect to login |
| MT-23 | API requires token | `GET http://localhost:8000/api/dashboard/summary` without a token (browser or curl) | 401 `{"detail":"Not authenticated"}`; `/docs` loads |
| MT-24 | Responsive layout | Resize browser to ~375 px wide | Navigation wraps, tables scroll horizontally, no clipped controls |

## Sign-off
| Build/commit | Tester | Date | Passed | Failed | Notes |
|---|---|---|---|---|---|
