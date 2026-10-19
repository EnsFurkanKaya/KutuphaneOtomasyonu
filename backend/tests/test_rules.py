"""Saf iş kuralı fonksiyonlarının birim testleri."""
from datetime import datetime, timedelta, timezone
import pytest

from app.domain import rules
from app.domain.enums import LoanStatus, Role
from app.domain.errors import BusinessRuleError, ConflictError, PermissionDeniedError


def test_calculate_due_date() -> None:
    """Kural 1: Varsayılan 14 gün veya yapılandırılan ödünç süresi."""
    now = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
    due = rules.calculate_due_date(now, 14)
    assert due == datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)

    with pytest.raises(BusinessRuleError):
        rules.calculate_due_date(now, 0)


def test_is_overdue_and_days() -> None:
    """Kural 9, 10, 11: Gecikme hesaplaması."""
    due = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
    before_due = datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc)
    after_due_2d = datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
    returned = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)

    # Henüz son iade tarihi gelmedi
    assert not rules.is_overdue(due, None, before_due)
    assert rules.overdue_days(due, None, before_due) == 0
    assert rules.loan_status(due, None, before_due) == LoanStatus.ACTIVE

    # Son iade tarihi 2 gün geçti ve iade edilmedi -> OVERDUE
    assert rules.is_overdue(due, None, after_due_2d)
    assert rules.overdue_days(due, None, after_due_2d) == 2
    assert rules.loan_status(due, None, after_due_2d) == LoanStatus.OVERDUE

    # İade edildi -> RETURNED, artık aktif gecikmiş değil
    assert not rules.is_overdue(due, returned, after_due_2d)
    assert rules.overdue_days(due, returned, after_due_2d) == 0
    assert rules.loan_status(due, returned, after_due_2d) == LoanStatus.RETURNED


def test_ensure_can_borrow_rules() -> None:
    """Kural 2, 3, 5, 13, 14 doğrulama kontrolleri."""
    # Başarılı durum
    rules.ensure_can_borrow(
        role=Role.STUDENT.value,
        user_is_active=True,
        active_loan_count=1,
        max_active_loans=3,
        book_is_active=True,
        available_copies=2,
        already_has_active_loan_for_book=False,
    )

    # Admin ödünç alamaz
    with pytest.raises(PermissionDeniedError):
        rules.ensure_can_borrow(
            role=Role.ADMIN.value,
            user_is_active=True,
            active_loan_count=0,
            max_active_loans=3,
            book_is_active=True,
            available_copies=2,
            already_has_active_loan_for_book=False,
        )

    # Pasif kullanıcı ödünç alamaz (Kural 13)
    with pytest.raises(BusinessRuleError):
        rules.ensure_can_borrow(
            role=Role.STUDENT.value,
            user_is_active=False,
            active_loan_count=0,
            max_active_loans=3,
            book_is_active=True,
            available_copies=2,
            already_has_active_loan_for_book=False,
        )

    # Limit aşıldı (Kural 2)
    with pytest.raises(BusinessRuleError):
        rules.ensure_can_borrow(
            role=Role.STUDENT.value,
            user_is_active=True,
            active_loan_count=3,
            max_active_loans=3,
            book_is_active=True,
            available_copies=2,
            already_has_active_loan_for_book=False,
        )

    # Kitap pasif (Kural 14)
    with pytest.raises(BusinessRuleError):
        rules.ensure_can_borrow(
            role=Role.STUDENT.value,
            user_is_active=True,
            active_loan_count=0,
            max_active_loans=3,
            book_is_active=False,
            available_copies=2,
            already_has_active_loan_for_book=False,
        )

    # Aynı kitap zaten ödünçte (Kural 5)
    with pytest.raises(ConflictError):
        rules.ensure_can_borrow(
            role=Role.STUDENT.value,
            user_is_active=True,
            active_loan_count=1,
            max_active_loans=3,
            book_is_active=True,
            available_copies=2,
            already_has_active_loan_for_book=True,
        )

    # Stok yok (Kural 3)
    with pytest.raises(BusinessRuleError):
        rules.ensure_can_borrow(
            role=Role.STUDENT.value,
            user_is_active=True,
            active_loan_count=0,
            max_active_loans=3,
            book_is_active=True,
            available_copies=0,
            already_has_active_loan_for_book=False,
        )


def test_calculate_available_after_stock_change() -> None:
    """Kural 4: Stok kuralı."""
    assert rules.calculate_available_after_stock_change(10, 3) == 7

    # Toplam ödünçte olandan az olamaz
    with pytest.raises(BusinessRuleError):
        rules.calculate_available_after_stock_change(2, 3)
