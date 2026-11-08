import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

_connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
# On serverless platforms (Vercel sets VERCEL=1) every invocation may be a new process, so keep no
# connection pool of our own and let Supabase's pooler do the pooling.
_pool_kwargs = {"poolclass": NullPool} if os.getenv("VERCEL") else {}
engine = create_engine(
    settings.database_url, connect_args=_connect_args, pool_pre_ping=True, **_pool_kwargs
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
