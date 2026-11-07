import pytest

from tests.conftest import PASSWORD

pytestmark = pytest.mark.api


def test_login_success(client, auth):
    auth("admin")
    r = client.post("/api/auth/login", data={"username": "admin_user", "password": PASSWORD})
    assert r.status_code == 200
    assert r.json()["role"] == "admin" and r.json()["token_type"] == "bearer"


def test_login_wrong_password(client, auth):
    auth("admin")
    r = client.post("/api/auth/login", data={"username": "admin_user", "password": "nope"})
    assert r.status_code == 401


def test_login_unknown_user(client):
    r = client.post("/api/auth/login", data={"username": "ghost", "password": "whatever1"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_profile(client, auth):
    r = client.get("/api/auth/me", headers=auth("auditor"))
    assert r.status_code == 200 and r.json()["role"] == "auditor"


def test_admin_can_create_user(client, auth):
    body = {
        "username": "new.user",
        "full_name": "New User",
        "password": "Str0ngPass!",
        "role": "officer",
    }
    r = client.post("/api/auth/users", json=body, headers=auth("admin"))
    assert r.status_code == 201 and "password" not in r.json()


def test_duplicate_username_conflict(client, auth):
    body = {
        "username": "dupe",
        "full_name": "Dupe User",
        "password": "Str0ngPass!",
        "role": "officer",
    }
    assert client.post("/api/auth/users", json=body, headers=auth("admin")).status_code == 201
    assert client.post("/api/auth/users", json=body, headers=auth("admin")).status_code == 409


def test_officer_cannot_create_user(client, auth):
    body = {"username": "x1x", "full_name": "X Y", "password": "Str0ngPass!", "role": "admin"}
    assert client.post("/api/auth/users", json=body, headers=auth("officer")).status_code == 403


def test_weak_password_rejected(client, auth):
    body = {"username": "weak", "full_name": "Weak One", "password": "short", "role": "officer"}
    assert client.post("/api/auth/users", json=body, headers=auth("admin")).status_code == 422
