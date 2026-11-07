import pytest

from app.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


def test_hash_is_salted_and_verifiable():
    h1, h2 = hash_password("secret123"), hash_password("secret123")
    assert h1 != h2
    assert verify_password("secret123", h1)


def test_wrong_password_rejected():
    assert not verify_password("wrong", hash_password("secret123"))


@pytest.mark.parametrize("stored", ["", "garbage", "a$b$c$d", "pbkdf2_sha256$x$zz$yy"])
def test_malformed_hash_is_rejected_not_raised(stored):
    assert verify_password("secret123", stored) is False


def test_token_roundtrip():
    payload = decode_token(create_access_token("alice", "admin"))
    assert payload["sub"] == "alice" and payload["role"] == "admin"


def test_expired_token_rejected():
    import jwt

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(create_access_token("alice", "admin", minutes=-1))


def test_tampered_token_rejected():
    import jwt

    token = create_access_token("alice", "admin")
    with pytest.raises(jwt.PyJWTError):
        decode_token(token[:-2] + ("AA" if not token.endswith("AA") else "BB"))
