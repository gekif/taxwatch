"""End-to-end smoke test against a RUNNING API (after migrations + seed).

Usage:
    python -m pip install httpx
    python -m scripts.smoke_test                       # defaults to http://localhost:8000
    API_URL=https://staging.example.com SMOKE_PASSWORD=... python -m scripts.smoke_test

Exits non-zero on the first failed check, so it can gate a deployment.
"""

import os
import sys
import uuid
from datetime import date

import httpx

API = os.getenv("API_URL", "http://localhost:8000")
PASSWORD = os.getenv("SMOKE_PASSWORD", "Demo#12345")


def check(label: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")
    if not condition:
        sys.exit(1)


def login(client: httpx.Client, username: str) -> dict:
    r = client.post("/api/auth/login", data={"username": username, "password": PASSWORD})
    check(f"login as {username}", r.status_code == 200)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def main() -> None:
    with httpx.Client(base_url=API, timeout=15) as c:
        check("health endpoint", c.get("/health").json() == {"status": "ok"})
        check("protected endpoint rejects anonymous", c.get("/api/dashboard/summary").status_code == 401)

        officer, auditor = login(c, "officer"), login(c, "auditor")
        npwpd = "SMK" + uuid.uuid4().hex[:8].upper()
        r = c.post(
            "/api/taxpayers",
            json={"npwpd": npwpd, "name": "Smoke Test Hotel", "category": "hotel"},
            headers=officer,
        )
        check("officer creates taxpayer", r.status_code == 201)
        tp_id = r.json()["id"]

        r = c.post(
            "/api/transactions",
            json={"taxpayer_id": tp_id, "amount": 60_000_000, "trx_date": date.today().isoformat()},
            headers=officer,
        )
        check("transaction created with 10% tax", r.status_code == 201 and r.json()["tax_amount"] == 6_000_000)
        check("large transaction is flagged", r.json()["is_flagged"] is True)
        trx_id = r.json()["id"]

        r = c.post(f"/api/transactions/{trx_id}/clear-flag", headers=officer)
        check("officer cannot clear flag", r.status_code == 403)
        r = c.post(f"/api/transactions/{trx_id}/clear-flag", headers=auditor)
        check("auditor clears flag", r.status_code == 200 and r.json()["is_flagged"] is False)

        r = c.get("/api/dashboard/summary", headers=auditor)
        check("dashboard summary available", r.status_code == 200 and r.json()["transactions"] > 0)
        r = c.get("/api/audit", headers=auditor)
        check("audit trail readable by auditor", r.status_code == 200 and r.json()["total"] > 0)
    print("\nSmoke test passed.")


if __name__ == "__main__":
    main()
