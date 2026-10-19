"""Veritabanı bağlantısı, oturum fabrikası ve transaction yardımcıları."""
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
if "sqlite" not in settings.database_url:
    engine_kwargs.update({"pool_size": 10, "max_overflow": 10})

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI bağımlılığı: istek başına bir oturum açar ve kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def transaction(session: Session) -> Iterator[Session]:
    """Bloğu tek bir transaction olarak çalıştırır: başarıda commit, hatada rollback."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
