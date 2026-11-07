import pytest

pytestmark = pytest.mark.api


def test_create_and_get(client, auth, make_taxpayer):
    tp = make_taxpayer()
    r = client.get(f"/api/taxpayers/{tp['id']}", headers=auth("auditor"))
    assert r.status_code == 200 and r.json()["npwpd"] == "HTL000001"


def test_duplicate_npwpd_conflict(client, auth, make_taxpayer):
    make_taxpayer()
    r = client.post(
        "/api/taxpayers",
        json={"npwpd": "HTL000001", "name": "Other", "category": "hotel"},
        headers=auth("admin"),
    )
    assert r.status_code == 409


@pytest.mark.parametrize("npwpd", ["abc", "lowercase1", "TOO-LONG-NPWPD-0000000000", "HT L1234"])
def test_invalid_npwpd_rejected(client, auth, npwpd):
    r = client.post(
        "/api/taxpayers",
        json={"npwpd": npwpd, "name": "Name", "category": "hotel"},
        headers=auth("admin"),
    )
    assert r.status_code == 422


def test_invalid_category_rejected(client, auth):
    r = client.post(
        "/api/taxpayers",
        json={"npwpd": "ABC12345", "name": "Name", "category": "casino"},
        headers=auth("admin"),
    )
    assert r.status_code == 422


def test_list_search_and_pagination(client, auth, make_taxpayer):
    make_taxpayer("HTL000001", "hotel", "Alpha Hotel")
    make_taxpayer("RST000001", "restoran", "Beta Resto")
    make_taxpayer("RST000002", "restoran", "Gamma Resto")
    h = auth("auditor")
    assert client.get("/api/taxpayers", headers=h).json()["total"] == 3
    assert client.get("/api/taxpayers?q=resto", headers=h).json()["total"] == 2
    page = client.get("/api/taxpayers?limit=2&skip=2", headers=h).json()
    assert page["total"] == 3 and len(page["items"]) == 1


def test_update_taxpayer(client, auth, make_taxpayer):
    tp = make_taxpayer()
    r = client.put(f"/api/taxpayers/{tp['id']}", json={"name": "Renamed"}, headers=auth("officer"))
    assert r.status_code == 200 and r.json()["name"] == "Renamed"


def test_not_found(client, auth):
    assert client.get("/api/taxpayers/999", headers=auth("admin")).status_code == 404


def test_soft_delete_hides_taxpayer(client, auth, make_taxpayer):
    tp = make_taxpayer()
    assert client.delete(f"/api/taxpayers/{tp['id']}", headers=auth("admin")).status_code == 204
    assert client.get(f"/api/taxpayers/{tp['id']}", headers=auth("admin")).status_code == 404
    assert client.get("/api/taxpayers", headers=auth("admin")).json()["total"] == 0


def test_role_restrictions(client, auth, make_taxpayer):
    tp = make_taxpayer()
    body = {"npwpd": "NEW12345", "name": "Name", "category": "parkir"}
    assert client.post("/api/taxpayers", json=body, headers=auth("auditor")).status_code == 403
    assert client.delete(f"/api/taxpayers/{tp['id']}", headers=auth("officer")).status_code == 403
    assert client.get("/api/taxpayers").status_code == 401
