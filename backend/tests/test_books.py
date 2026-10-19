"""Kitap ve kategori testleri."""
from fastapi.testclient import TestClient
from app.models.book import Book
from app.models.category import Category


def test_student_list_books(client: TestClient, student_headers: dict[str, str], sample_book: Book) -> None:
    """Senaryo 4: Öğrencinin kitap listesini görüntülemesi ve arama yapabilmesi."""
    response = client.get("/api/books", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert any(b["isbn"] == sample_book.isbn for b in data["items"])

    # Arama ile filtreleme
    search_resp = client.get("/api/books?q=Temiz", headers=student_headers)
    assert search_resp.status_code == 200
    assert len(search_resp.json()["items"]) >= 1

    # Bulunamayan arama
    search_empty = client.get("/api/books?q=MevcutOlmayanKitapXyz", headers=student_headers)
    assert search_empty.status_code == 200
    assert len(search_empty.json()["items"]) == 0


def test_admin_create_book_success(client: TestClient, admin_headers: dict[str, str], sample_category: Category) -> None:
    """Senaryo 5: Yönetici tarafından yeni kitap eklenmesi."""
    payload = {
        "isbn": "9789750719387",
        "title": "Kürk Mantolu Madonna",
        "author": "Sabahattin Ali",
        "publisher": "YKY",
        "publication_year": 2019,
        "category_id": sample_category.id,
        "shelf_location": "B-201",
        "total_copies": 5,
        "description": "Klasik Türk edebiyatı başyapıtı.",
    }
    response = client.post("/api/books", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Kürk Mantolu Madonna"
    assert data["total_copies"] == 5
    assert data["available_copies"] == 5
    assert data["is_available"] is True
    assert data["category"]["id"] == sample_category.id


def test_student_cannot_access_admin_book_create(
    client: TestClient, student_headers: dict[str, str], sample_category: Category
) -> None:
    """Senaryo 14: Öğrencinin yönetici endpoint'ine erişememesi (403 Forbidden)."""
    payload = {
        "isbn": "9789750719394",
        "title": "İzinsiz Kitap",
        "author": "Yazar",
        "total_copies": 1,
    }
    response = client.post("/api/books", json=payload, headers=student_headers)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "YONETICI_YETKISI_GEREKLI"


def test_student_cannot_access_admin_stock_update(
    client: TestClient, student_headers: dict[str, str], sample_book: Book
) -> None:
    """Öğrencinin stok güncelleme endpoint'ine erişememesi (403)."""
    response = client.patch(
        f"/api/books/{sample_book.id}/stock",
        json={"total_copies": 10},
        headers=student_headers,
    )
    assert response.status_code == 403


def test_admin_update_book_and_stock(
    client: TestClient, admin_headers: dict[str, str], sample_book: Book
) -> None:
    """Yöneticinin kitap bilgilerini ve stok sayısını güncellemesi."""
    # Bilgi güncelleme
    resp_update = client.patch(
        f"/api/books/{sample_book.id}",
        json={"shelf_location": "B-303"},
        headers=admin_headers,
    )
    assert resp_update.status_code == 200
    assert resp_update.json()["shelf_location"] == "B-303"

    # Stok güncelleme
    resp_stock = client.patch(
        f"/api/books/{sample_book.id}/stock",
        json={"total_copies": 10},
        headers=admin_headers,
    )
    assert resp_stock.status_code == 200
    assert resp_stock.json()["total_copies"] == 10
    assert resp_stock.json()["available_copies"] == 10
