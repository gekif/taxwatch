import os

# Must be set before the app is imported.
os.environ.setdefault("PASSWORD_HASH_ITERATIONS", "1000")  # fast hashing in tests
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-32b")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, select  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402
from app.security import hash_password  # noqa: E402

PASSWORD = "Passw0rd!"


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override():
        yield db_session

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth(client, db_session):
    """auth('admin') -> Authorization headers for a user with that role (created on demand)."""

    def _auth(role: str = "admin") -> dict:
        username = f"{role}_user"
        if not db_session.scalar(select(User).where(User.username == username)):
            db_session.add(
                User(
                    username=username,
                    full_name=role.title(),
                    role=role,
                    password_hash=hash_password(PASSWORD),
                )
            )
            db_session.commit()
        r = client.post("/api/auth/login", data={"username": username, "password": PASSWORD})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    return _auth


@pytest.fixture()
def make_taxpayer(client, auth):
    def _make(npwpd="HTL000001", category="hotel", name="Test Hotel"):
        r = client.post(
            "/api/taxpayers",
            json={"npwpd": npwpd, "name": name, "category": category},
            headers=auth("admin"),
        )
        assert r.status_code == 201, r.text
        return r.json()

    return _make


@pytest.fixture()
def make_trx(client, auth):
    def _make(taxpayer_id, amount=1_000_000, trx_date="2026-01-15", role="officer"):
        return client.post(
            "/api/transactions",
            json={"taxpayer_id": taxpayer_id, "amount": amount, "trx_date": trx_date},
            headers=auth(role),
        )

    return _make
