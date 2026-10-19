"""Gecikme raporu ve istatistik paneli testleri."""
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.category import Category
from app.models.loan import Loan
from app.models.user import User


def test_overdue_report_filters_and_calculations(
    client: TestClient,
    admin_headers: dict[str, str],
    student_headers: dict[str, str],
    student_user: User,
    sample_book: Book,
    db_session: Session,
) -> None:
    """Senaryo 12: Gecikmiş kayıtların doğru raporlanması (Kural 9, 10, 11)."""
    now = datetime.now(timezone.utc)

    # 1. Kayıt: Gecikmiş kayıt (Ödünç: 20 gün önce, Son İade: 6 gün önce, İade: None)
    overdue_loan = Loan(
        user_id=student_user.id,
        book_id=sample_book.id,
        borrowed_at=now - timedelta(days=20),
        due_at=now - timedelta(days=6),
        returned_at=None,
    )
    db_session.add(overdue_loan)

    # 2. Kayıt: İade edilmiş kayıt (Gecikmiş olmamalı!)
    returned_loan = Loan(
        user_id=student_user.id,
        book_id=sample_book.id,
        borrowed_at=now - timedelta(days=30),
        due_at=now - timedelta(days=16),
        returned_at=now - timedelta(days=15),
    )
    db_session.add(returned_loan)
    db_session.commit()

    # Yönetici gecikme raporunu ister
    report_resp = client.get("/api/reports/overdue", headers=admin_headers)
    assert report_resp.status_code == 200
    report_data = report_resp.json()

    # Yalnızca iade edilmemiş ve süresi geçmiş kayıt raporda olmalı
    assert report_data["total"] >= 1
    overdue_ids = [item["loan_id"] for item in report_data["items"]]
    assert overdue_loan.id in overdue_ids
    assert returned_loan.id not in overdue_ids  # Kural 11: İade edilen kayıt raporda yer almaz

    # Gecikme günü hesaplaması pozitif ve doğru olmalı
    matching_item = next(i for i in report_data["items"] if i["loan_id"] == overdue_loan.id)
    assert matching_item["overdue_days"] >= 6
    assert matching_item["student_number"] == student_user.student_number
    assert matching_item["book_title"] == sample_book.title


def test_student_cannot_access_reports(
    client: TestClient, student_headers: dict[str, str]
) -> None:
    """Öğrencinin rapor endpoint'lerine erişememesi (403)."""
    resp1 = client.get("/api/reports/overdue", headers=student_headers)
    assert resp1.status_code == 403

    resp2 = client.get("/api/reports/dashboard", headers=student_headers)
    assert resp2.status_code == 403


def test_dashboard_stats(
    client: TestClient, admin_headers: dict[str, str], sample_book: Book
) -> None:
    """Yönetici dashboard istatistiklerinin kontrolü."""
    response = client.get("/api/reports/dashboard", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["active_book_titles"] >= 1
    assert data["total_copies"] >= 3
    assert data["available_copies"] >= 0
    assert "recent_activity" in data
