"""Application settings, read from environment variables (12-factor)."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

# Load backend/.env (or a parent .env) if present. Real environment variables always win,
# so CI, Docker and the test suite are unaffected.
load_dotenv()

DEFAULT_SECRET = "dev-secret-change-me"


def _origins() -> list[str]:
    return [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o]


@dataclass(frozen=True)
class Settings:
    env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./taxwatch.db")
    secret_key: str = os.getenv("SECRET_KEY", DEFAULT_SECRET)
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
    password_hash_iterations: int = int(os.getenv("PASSWORD_HASH_ITERATIONS", "200000"))
    anomaly_threshold: int = int(os.getenv("ANOMALY_THRESHOLD", "50000000"))  # IDR
    cors_origins: list[str] = field(default_factory=_origins)


def validate_settings(s: Settings) -> None:
    """Fail fast on unsafe production configuration."""
    if s.env == "production" and (s.secret_key == DEFAULT_SECRET or len(s.secret_key) < 32):
        raise RuntimeError("SECRET_KEY must be set to a random value of 32+ chars in production")


settings = Settings()
