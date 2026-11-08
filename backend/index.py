"""Vercel entrypoint: exposes the FastAPI instance as `app` at the project root."""

from app.main import app

__all__ = ["app"]
