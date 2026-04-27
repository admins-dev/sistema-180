"""
Database engine and session management.

SQLite with WAL mode for concurrent read/write.
Designed to be portable to PostgreSQL later.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import get_settings
from app.domain.models.base import Base

# Import all models so Base.metadata knows about them
from app.domain.models import lead, enrichment, scoring, job, outreach  # noqa: F401


_engine = None
_SessionFactory = None


def get_engine():
    """Get or create the SQLAlchemy engine (singleton)."""
    global _engine
    if _engine is None:
        settings = get_settings()
        db_url = f"sqlite:///{settings.db_path}"
        _engine = create_engine(
            db_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"check_same_thread": False},
        )

        # Enable WAL mode for concurrent read/write
        @event.listens_for(_engine, "connect")
        def _set_sqlite_pragmas(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return _engine


def get_session_factory() -> sessionmaker:
    """Get or create the session factory (singleton)."""
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _SessionFactory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions with auto-commit/rollback."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Create all tables. Safe to call multiple times (CREATE IF NOT EXISTS)."""
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_db() -> None:
    """Drop all tables. DANGER: only for testing."""
    engine = get_engine()
    Base.metadata.drop_all(engine)


def get_db_stats() -> dict:
    """Quick health check: table counts."""
    with get_session() as session:
        stats = {}
        for table_name in Base.metadata.tables:
            result = session.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            )
            stats[table_name] = result.scalar()
        return stats
