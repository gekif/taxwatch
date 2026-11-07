import pytest

pytestmark = pytest.mark.api


def test_summary_empty(client, auth):
    body = client.get("/api/dashboard/summary", headers=auth("admin")).json()
    assert body["transactions"] == 0 and body["total_tax"] == 0 and body["monthly"] == []


def test_summary_aggregates(client, auth, make_taxpayer, make_trx):
    hotel = make_taxpayer("HTL000001", "hotel", "Hotel H")
    resto = make_taxpayer("RST000001", "restoran", "Resto R")
    make_trx(hotel["id"], 1_000_000, "2026-01-10")
    make_trx(resto["id"], 500_000, "2026-01-20")
    make_trx(resto["id"], 60_000_000, "2026-02-05")
    body = client.get("/api/dashboard/summary", headers=auth("auditor")).json()
    assert body["taxpayers"] == 2 and body["transactions"] == 3 and body["flagged"] == 1
    assert body["total_amount"] == 61_500_000
    assert [m["month"] for m in body["monthly"]] == ["2026-01", "2026-02"]
    cats = {c["category"]: c for c in body["by_category"]}
    assert cats["hotel"]["tax"] == 100_000 and cats["restoran"]["transactions"] == 2


def test_summary_requires_auth(client):
    assert client.get("/api/dashboard/summary").status_code == 401


def test_audit_trail_records_actions(client, auth, make_taxpayer, make_trx):
    tp = make_taxpayer()
    make_trx(tp["id"])
    items = client.get("/api/audit", headers=auth("auditor")).json()["items"]
    actions = {(i["action"], i["entity"]) for i in items}
    assert ("create", "taxpayer") in actions and ("create", "transaction") in actions


def test_officer_cannot_read_audit(client, auth):
    assert client.get("/api/audit", headers=auth("officer")).status_code == 403


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
