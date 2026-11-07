"""Password hashing (PBKDF2-HMAC-SHA256, stdlib) and JWT helpers."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from .config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    iterations = settings.password_hash_iterations
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt, digest = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
        )
        return hmac.compare_digest(candidate.hex(), digest)
    except (ValueError, TypeError):
        return False


def create_access_token(username: str, role: str, minutes: int | None = None) -> str:
    minutes = settings.access_token_minutes if minutes is None else minutes
    expire = datetime.now(UTC) + timedelta(minutes=minutes)
    payload = {"sub": username, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
