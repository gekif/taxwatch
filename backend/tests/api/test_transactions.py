import pytest

pytestmark = pytest.mark.api


def test_create_calculates_tax(make_taxpayer, make_trx):
    tp = make_taxpayer(category="hiburan")
    r = make_trx(tp["id"], amount=2_000_000)
    assert r.status_code == 201
    body = r.json()
    assert body["tax_amount"] == 300_000 and body["is_flagged"] is False
    assert body["taxpayer_name"] == "Test Hotel"


def test_amount_above_threshold_is_flagged(make_taxpayer, make_trx):
    tp = make_taxpayer()
    body = make_trx(tp["id"], amount=60_000_000).json()
    assert body["is_flagged"] is True and body["flag_reason"] == "above_threshold"


def test_spike_vs_history_is_flagged(make_taxpayer, make_trx):
    tp = make_taxpayer()
    for _ in range(5):
        make_trx(tp["id"], amount=1_000_000)
    body = make_trx(tp["id"], amount=5_000_000).json()
    assert body["flag_reason"] == "spike_vs_average"


def test_unknown_taxpayer(make_trx):
    assert make_trx(999).status_code == 404


@pytest.mark.parametrize("amount", [0, -5])
def test_non_positive_amount_rejected(make_taxpayer, make_trx, amount):
    assert make_trx(make_taxpayer()["id"], amount=amount).status_code == 422


def test_filters(client, auth, make_taxpayer, make_trx):
    tp = make_taxpayer()
    make_trx(tp["id"], 1_000_000, "2026-01-10")
    make_trx(tp["id"], 2_000_000, "2026-02-10")
    make_trx(tp["id"], 60_000_000, "2026-03-10")
    h = auth("auditor")
    assert client.get("/api/transactions", headers=h).json()["total"] == 3
    assert client.get("/api/transactions?flagged_only=true", headers=h).json()["total"] == 1
    r = client.get("/api/transactions?date_from=2026-02-01&date_to=2026-02-28", headers=h).json()
    assert r["total"] == 1 and r["items"][0]["amount"] == 2_000_000


def test_list_sorted_newest_first(client, auth, make_taxpayer, make_trx):
    tp = make_taxpayer()
    make_trx(tp["id"], 1_000_000, "2026-01-10")
    make_trx(tp["id"], 1_000_000, "2026-02-10")
    dates = [
        i["trx_date"]
        for i in client.get("/api/transactions", headers=auth("admin")).json()["items"]
    ]
    assert dates == sorted(dates, reverse=True)


def test_auditor_clears_flag(client, auth, make_taxpayer, make_trx):
    trx = make_trx(make_taxpayer()["id"], 60_000_000).json()
    r = client.post(f"/api/transactions/{trx['id']}/clear-flag", headers=auth("auditor"))
    assert r.status_code == 200 and r.json()["is_flagged"] is False


def test_officer_cannot_clear_flag(client, auth, make_taxpayer, make_trx):
    trx = make_trx(make_taxpayer()["id"], 60_000_000).json()
    assert (
        client.post(
            f"/api/transactions/{trx['id']}/clear-flag", headers=auth("officer")
        ).status_code
        == 403
    )


def test_trx_date_allows_one_day_timezone_tolerance(make_taxpayer, make_trx):
    from datetime import date, timedelta

    tp = make_taxpayer()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    in_two_days = (date.today() + timedelta(days=2)).isoformat()
    assert make_trx(tp["id"], trx_date=tomorrow).status_code == 201
    assert make_trx(tp["id"], trx_date=in_two_days).status_code == 422
