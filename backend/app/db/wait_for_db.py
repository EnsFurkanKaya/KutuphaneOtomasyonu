"""API başlamadan önce veritabanının bağlantı kabul etmesini bekler."""
import sys
import time

from sqlalchemy import text

from app.db.session import engine


def wait_for_db(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Veritabanı hazır.")
            return
        except Exception:  # noqa: BLE001 - bağlantı hatalarının tamamı yeniden denenir
            print(f"Veritabanı bekleniyor... ({attempt}/{max_attempts})")
            time.sleep(delay_seconds)
    print("Veritabanına bağlanılamadı.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    wait_for_db()
