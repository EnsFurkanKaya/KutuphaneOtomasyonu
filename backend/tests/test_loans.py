"""Ödünç alma ve iade işlem senaryoları testleri."""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.category import Category
from app.models.user import User


def test_student_borrows_available_book_success(
    client: TestClient, student_headers: dict[str, str], sample_book: Book
) -> None:
    """Senaryo 6: Öğrencinin uygun kitabı ödünç alması; stok 1 azalır."""
    initial_available = sample_book.available_copies
    response = client.post(
        "/api/loans",
        json={"book_id": sample_book.id},
        headers=student_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["book"]["id"] == sample_book.id
    assert data["status"] == "ACTIVE"
    assert data["returned_at"] is None

    # Kitap stoğu kontrolü (1 azalmalı)
    book_resp = client.get(f"/api/books/{sample_book.id}", headers=student_headers)
    assert book_resp.status_code == 200
    assert book_resp.json()["available_copies"] == initial_available - 1


def test_borrow_fails_when_out_of_stock(
    client: TestClient,
    admin_headers: dict[str, str],
    student_headers: dict[str, str],
    sample_category: Category,
) -> None:
    """Senaryo 7: Stokta kitap yokken ödünç işleminin reddedilmesi (400)."""
    # 0 stoklu kitap oluştur
    create_resp = client.post(
        "/api/books",
        json={
            "isbn": "9789750000010",
            "title": "Tükenmiş Kitap",
            "author": "Yazar",
            "total_copies": 0,
            "category_id": sample_category.id,
        },
        headers=admin_headers,
    )
    book_id = create_resp.json()["id"]

    # Ödünç alma isteği
    resp = client.post("/api/loans", json={"book_id": book_id}, headers=student_headers)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] in ("IS_KURALI_IHLALI", "STOK_YOK")
    assert "kopyası yok" in resp.json()["error"]["message"]


def test_borrow_fails_when_limit_exceeded(
    client: TestClient,
    admin_headers: dict[str, str],
    student_headers: dict[str, str],
    sample_category: Category,
) -> None:
    """Senaryo 8: Öğrenci ödünç limitini (en fazla 3) aştığında işlemin reddedilmesi."""
    # 4 ayrı kitap oluştur
    book_ids = []
    for i in range(1, 5):
        resp = client.post(
            "/api/books",
            json={
                "isbn": f"97897500000{i}1",
                "title": f"Limit Kitabı {i}",
                "author": "Yazar",
                "total_copies": 2,
                "category_id": sample_category.id,
            },
            headers=admin_headers,
        )
        book_ids.append(resp.json()["id"])

    # İlk 3 kitabı başarıyla ödünç al
    for b_id in book_ids[:3]:
        r = client.post("/api/loans", json={"book_id": b_id}, headers=student_headers)
        assert r.status_code == 201

    # 4. kitap denemesi limit ihlali nedeniyle 400 dönmeli
    resp4 = client.post("/api/loans", json={"book_id": book_ids[3]}, headers=student_headers)
    assert resp4.status_code == 400
    assert resp4.json()["error"]["code"] == "ODUNC_LIMITI_ASILDI"


def test_borrow_duplicate_active_book_fails(
    client: TestClient, student_headers: dict[str, str], sample_book: Book
) -> None:
    """Senaryo 9: Aynı öğrencinin aynı kitaba ilişkin ikinci aktif ödünç işleminin engellenmesi."""
    # İlk ödünç
    resp1 = client.post("/api/loans", json={"book_id": sample_book.id}, headers=student_headers)
    assert resp1.status_code == 201

    # İkinci ödünç
    resp2 = client.post("/api/loans", json={"book_id": sample_book.id}, headers=student_headers)
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "AYNI_KITAP_ZATEN_ODUNCTE"


def test_return_book_increases_stock_once_only(
    client: TestClient, student_headers: dict[str, str], sample_book: Book
) -> None:
    """Senaryo 10 & 11: İade işleminde stok 1 artar; aynı kayıt ikinci kez iade edilemez (409)."""
    book_id = sample_book.id

    # Ödünç al
    borrow_resp = client.post("/api/loans", json={"book_id": book_id}, headers=student_headers)
    assert borrow_resp.status_code == 201
    loan_id = borrow_resp.json()["id"]

    # Ödünç sonrası stok
    book_after_borrow = client.get(f"/api/books/{book_id}", headers=student_headers).json()
    avail_after_borrow = book_after_borrow["available_copies"]

    # İade et
    return_resp = client.post(f"/api/loans/{loan_id}/return", headers=student_headers)
    assert return_resp.status_code == 200
    assert return_resp.json()["status"] == "RETURNED"
    assert return_resp.json()["returned_at"] is not None

    # Stok 1 artmış olmalı
    book_after_return = client.get(f"/api/books/{book_id}", headers=student_headers).json()
    assert book_after_return["available_copies"] == avail_after_borrow + 1

    # İkinci kez iade denemesi -> 409 Conflict
    return_again = client.post(f"/api/loans/{loan_id}/return", headers=student_headers)
    assert return_again.status_code == 409
    assert return_again.json()["error"]["code"] == "ZATEN_IADE_EDILDI"

    # Stok değişmemeli
    book_after_second = client.get(f"/api/books/{book_id}", headers=student_headers).json()
    assert book_after_second["available_copies"] == avail_after_borrow + 1


def test_student_cannot_access_other_student_loan(
    client: TestClient,
    student_headers: dict[str, str],
    student_2_headers: dict[str, str],
    sample_book: Book,
) -> None:
    """Senaryo 13: Öğrencinin başka bir öğrencinin ödünç kayıtlarına erişememesi (403)."""
    # 1. öğrenci ödünç alır
    borrow_resp = client.post("/api/loans", json={"book_id": sample_book.id}, headers=student_headers)
    loan_id = borrow_resp.json()["id"]

    # 2. öğrenci bu ödünç kaydını görüntülemeye çalışır
    view_resp = client.get(f"/api/loans/{loan_id}", headers=student_2_headers)
    assert view_resp.status_code == 403
    assert view_resp.json()["error"]["code"] == "KAYIT_SIZE_AIT_DEGIL"

    # 2. öğrenci bu ödünç kaydını iade etmeye çalışır
    return_resp = client.post(f"/api/loans/{loan_id}/return", headers=student_2_headers)
    assert return_resp.status_code == 403
    assert return_resp.json()["error"]["code"] == "KAYIT_SIZE_AIT_DEGIL"
