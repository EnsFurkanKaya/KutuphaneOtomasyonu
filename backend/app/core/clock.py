"""Zaman yardımcıları. Tüm zaman damgaları UTC olarak saklanır."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
