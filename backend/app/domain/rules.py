"""Saf iş kuralları.

Bu modül veritabanı, HTTP veya framework bilmez; yalnızca değerler üzerinde
çalışır. Böylece kurallar kolayca test edilir ve tekrar kullanılır.
"""
import math
from datetime import datetime, timedelta, timezone

from app.domain.enums import LoanStatus, Role
from app.domain.errors import BusinessRuleError, ConflictError, PermissionDeniedError

SECONDS_PER_DAY = 86_400


def _normalize_dt(dt: datetime) -> datetime:
    """Offset-naive ve offset-aware datetime karşılaştırmalarını güvenli kılar."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def calculate_due_date(borrowed_at: datetime, loan_period_days: int) -> datetime:
    """Kural 1: Son iade tarihi = ödünç tarihi + ödünç süresi (varsayılan 14 gün)."""
    if loan_period_days < 1:
        raise BusinessRuleError("Ödünç süresi en az 1 gün olmalıdır.", "GECERSIZ_ODUNC_SURESI")
    return borrowed_at + timedelta(days=loan_period_days)


def is_overdue(due_at: datetime, returned_at: datetime | None, now: datetime) -> bool:
    """Kural 9-11: İade edilmemiş ve son iade tarihi geçmiş kayıt gecikmiştir."""
    return returned_at is None and _normalize_dt(now) > _normalize_dt(due_at)


def overdue_days(due_at: datetime, returned_at: datetime | None, now: datetime) -> int:
    """Aktif gecikme günü. İade edilmiş veya gecikmemiş kayıtlar için 0, asla negatif değil.

    Son iade tarihinden sonra başlayan her 24 saatlik dilim (kısmi dahil) 1 gün sayılır.
    """
    if not is_overdue(due_at, returned_at, now):
        return 0
    diff = (_normalize_dt(now) - _normalize_dt(due_at)).total_seconds()
    return max(1, math.ceil(diff / SECONDS_PER_DAY))


def late_return_days(due_at: datetime, returned_at: datetime | None) -> int:
    """Geçmiş kayıtlar için: kitap geç iade edildiyse kaç gün geç kaldı (asla negatif değil)."""
    if returned_at is None or _normalize_dt(returned_at) <= _normalize_dt(due_at):
        return 0
    diff = (_normalize_dt(returned_at) - _normalize_dt(due_at)).total_seconds()
    return max(1, math.ceil(diff / SECONDS_PER_DAY))


def loan_status(due_at: datetime, returned_at: datetime | None, now: datetime) -> LoanStatus:
    if returned_at is not None:
        return LoanStatus.RETURNED
    return LoanStatus.OVERDUE if is_overdue(due_at, returned_at, now) else LoanStatus.ACTIVE


def ensure_can_borrow(
    *,
    role: str,
    user_is_active: bool,
    active_loan_count: int,
    max_active_loans: int,
    book_is_active: bool,
    available_copies: int,
    already_has_active_loan_for_book: bool,
) -> None:
    """Ödünç alma ön koşullarını doğrular (Kural 2, 3, 5, 13, 14)."""
    if role != Role.STUDENT.value:
        raise PermissionDeniedError("Yalnızca öğrenciler kitap ödünç alabilir.", "SADECE_OGRENCI")
    if not user_is_active:
        raise BusinessRuleError("Hesabınız pasif durumda olduğu için yeni kitap ödünç alamazsınız.", "KULLANICI_PASIF")
    if active_loan_count >= max_active_loans:
        raise BusinessRuleError(
            f"Aynı anda en fazla {max_active_loans} kitap ödünç alabilirsiniz.", "ODUNC_LIMITI_ASILDI"
        )
    if not book_is_active:
        raise BusinessRuleError("Bu kitap pasif durumda olduğu için ödünç verilemez.", "KITAP_PASIF")
    if already_has_active_loan_for_book:
        raise ConflictError("Bu kitabın bir kopyası zaten sizde ödünçte.", "AYNI_KITAP_ZATEN_ODUNCTE")
    if available_copies <= 0:
        raise BusinessRuleError("Bu kitabın şu anda ödünç verilebilecek uygun kopyası yok.", "STOK_YOK")


def calculate_available_after_stock_change(new_total: int, active_loan_count: int) -> int:
    """Kural 4: Toplam kopya, ödünçteki kopyalardan az olamaz; mevcut stok negatif olamaz."""
    if new_total < 0:
        raise BusinessRuleError("Toplam kopya sayısı negatif olamaz.", "GECERSIZ_STOK")
    if new_total < active_loan_count:
        raise BusinessRuleError(
            f"Toplam kopya sayısı, şu anda ödünçte olan {active_loan_count} kopyadan az olamaz.",
            "STOK_ODUNCTEKINDEN_AZ",
        )
    return new_total - active_loan_count
