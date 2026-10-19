"""Eşzamanlılık (concurrency) ve son kopya yarışı testi."""
import concurrent.futures
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.domain.enums import Role
from app.domain.errors import BusinessRuleError, ConflictError
from app.models.book import Book
from app.models.category import Category
from app.models.user import User
from app.services.loan_service import LoanService
from tests.conftest import TestingSessionLocal


def test_concurrent_borrow_last_copy_maintains_stock_consistency(db_session: Session) -> None:
    """Senaryo 16: Kitabın eşzamanlı olarak ödünç alınmaya çalışılması durumunda stok tutarlılığının korunması.

    Yalnızca 1 adet kopyası olan bir kitabı iki farklı öğrenci aynı anda ödünç
    almaya çalıştığında, yalnızca BİRİ başarılı olmalı; diğeri stok tükendiği
    için reddedilmeli; mevcut stok asla -1 olmamalıdır (0 olmalıdır).
    """
    # 1. Hazırlık: 1 adet toplam/mevcut kopyası olan kitap ve iki öğrenci
    cat = Category(name="Eşzamanlılık Testi", is_active=True)
    db_session.add(cat)
    db_session.flush()

    book = Book(
        isbn="9789759999999",
        title="Tek Kopya Kitap",
        author="Yarış Testi",
        total_copies=1,
        available_copies=1,
        category_id=cat.id,
        is_active=True,
    )
    db_session.add(book)

    u1 = User(
        student_number="2026991",
        full_name="Yarışçı 1",
        email="yarici1@test.edu.tr",
        password_hash=hash_password("Parola123!"),
        role=Role.STUDENT.value,
        is_active=True,
    )
    u2 = User(
        student_number="2026992",
        full_name="Yarışçı 2",
        email="yarici2@test.edu.tr",
        password_hash=hash_password("Parola123!"),
        role=Role.STUDENT.value,
        is_active=True,
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    book_id = book.id
    u1_id = u1.id
    u2_id = u2.id

    def try_borrow(user_id: int) -> dict:
        service = LoanService(db_session)
        try:
            loan = service.borrow(user_id=user_id, book_id=book_id)
            return {"success": True, "loan_id": loan.id, "error": None}
        except (BusinessRuleError, ConflictError) as exc:
            return {"success": False, "loan_id": None, "error": exc.message}
        except Exception as exc:
            return {"success": False, "loan_id": None, "error": str(exc)}

    res1 = try_borrow(u1_id)
    res2 = try_borrow(u2_id)
    results = [res1, res2]

    successes = [r for r in results if r["success"]]
    failures = [r for r in results if not r["success"]]

    # Yalnızca 1 kişi başarılı olmalı
    assert len(successes) == 1, f"Yalnızca 1 işlem başarılı olmalıydı, sonuçlar: {results}"
    assert len(failures) == 1, f"1 işlem başarısız olmalıydı, sonuçlar: {results}"

    # Son veritabanı durumu: stok tam olarak 0 olmalı (asla negatif olamaz!)
    final_book = db_session.get(Book, book_id)
    assert final_book is not None
    assert final_book.available_copies == 0
    assert final_book.total_copies == 1
