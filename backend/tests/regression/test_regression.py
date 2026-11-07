"""Baseline regression suite. Each test is tagged REG-xxx and mapped in docs/TEST_PLAN.md.

Rule: every bug fixed in future gets a new REG test *before* the fix is merged.
"""

import pytest

from app.models import User

pytestmark = pytest.mark.regression


def test_reg001_tax_rounding_is_half_up_integer(make_taxpayer, make_trx):
    tp = make_taxpayer()
    assert make_trx(tp["id"], amount=1_005).json()["tax_amount"] == 101


def test_reg002_future_dated_transaction_rejected(make_taxpayer, make_trx):
    tp = make_taxpayer()
    assert make_trx(tp["id"], trx_date="2999-01-01").status_code == 422


def test_reg003_deleted_taxpayer_cannot_receive_transactions(client, auth, make_taxpayer, make_trx):
    tp = make_taxpayer()
    client.delete(f"/api/taxpayers/{tp['id']}", headers=auth("admin"))
    assert make_trx(tp["id"]).status_code == 404


def test_reg004_duplicate_npwpd_is_409_not_500(client, auth, make_taxpayer):
    make_taxpayer()
    r = client.post(
        "/api/taxpayers",
        json={"npwpd": "HTL000001", "name": "Dup", "category": "hotel"},
        headers=auth("admin"),
    )
    assert r.status_code == 409


def test_reg005_auditor_is_read_only_for_transactions(make_taxpayer, make_trx):
    tp = make_taxpayer()
    assert make_trx(tp["id"], role="auditor").status_code == 403


def test_reg006_flag_cannot_be_cleared_twice(client, auth, make_taxpayer, make_trx):
    trx = make_trx(make_taxpayer()["id"], 60_000_000).json()
    url = f"/api/transactions/{trx['id']}/clear-flag"
    assert client.post(url, headers=auth("admin")).status_code == 200
    assert client.post(url, headers=auth("admin")).status_code == 409


def test_reg007_page_size_is_capped(client, auth):
    assert client.get("/api/transactions?limit=1000", headers=auth("admin")).status_code == 422


def test_reg008_deactivated_user_token_is_rejected(client, auth, db_session):
    headers = auth("officer")
    db_session.query(User).filter_by(username="officer_user").update({"is_active": False})
    db_session.commit()
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_reg009_password_hash_never_exposed(client, auth):
    assert "password" not in client.get("/api/auth/me", headers=auth("admin")).text


def test_reg010_clearing_a_flag_leaves_audit_record(client, auth, make_taxpayer, make_trx):
    trx = make_trx(make_taxpayer()["id"], 60_000_000).json()
    client.post(f"/api/transactions/{trx['id']}/clear-flag", headers=auth("auditor"))
    items = client.get("/api/audit", headers=auth("admin")).json()["items"]
    assert any(i["action"] == "clear_flag" and i["entity_id"] == trx["id"] for i in items)
