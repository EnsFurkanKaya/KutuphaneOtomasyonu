"""Kimlik doğrulama ve kullanıcı testleri."""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_student_registration_success(client: TestClient) -> None:
    """Senaryo 1: Yeni öğrencinin başarıyla kayıt olması."""
    payload = {
        "student_number": "2026555",
        "full_name": "Deniz Arda",
        "email": "deniz.arda@ogr.edu.tr",
        "password": "GucluParola123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_number"] == "2026555"
    assert data["email"] == "deniz.arda@ogr.edu.tr"
    assert data["role"] == "STUDENT"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_registration_duplicate_email_fails(client: TestClient) -> None:
    """Senaryo 2: Aynı e-posta adresiyle ikinci kez kayıt girişiminin reddedilmesi."""
    payload = {
        "student_number": "2026601",
        "full_name": "İlk Kullanıcı",
        "email": "ayni.eposta@ogr.edu.tr",
        "password": "Parola123!",
    }
    resp1 = client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    # Aynı e-posta, farklı öğrenci no
    payload2 = {
        "student_number": "2026602",
        "full_name": "İkinci Kullanıcı",
        "email": "ayni.eposta@ogr.edu.tr",
        "password": "Parola123!",
    }
    resp2 = client.post("/api/auth/register", json=payload2)
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "EPOSTA_KULLANIMDA"


def test_registration_duplicate_student_number_fails(client: TestClient) -> None:
    """Aynı öğrenci numarası ile ikinci kez kayıt girişiminin reddedilmesi."""
    payload1 = {
        "student_number": "2026701",
        "full_name": "Ali Veli",
        "email": "ali.veli@ogr.edu.tr",
        "password": "Parola123!",
    }
    assert client.post("/api/auth/register", json=payload1).status_code == 201

    payload2 = {
        "student_number": "2026701",
        "full_name": "Veli Ali",
        "email": "veli.ali@ogr.edu.tr",
        "password": "Parola123!",
    }
    resp = client.post("/api/auth/register", json=payload2)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "OGRENCI_NO_KULLANIMDA"


def test_login_correct_and_wrong_password(client: TestClient, student_user: User) -> None:
    """Senaryo 3: Doğru ve yanlış parolayla giriş."""
    # Yanlış parola
    resp_wrong = client.post(
        "/api/auth/login",
        json={"email": student_user.email, "password": "YanlisParola123!"},
    )
    assert resp_wrong.status_code == 401
    assert resp_wrong.json()["error"]["code"] == "GECERSIZ_KIMLIK_BILGISI"

    # Doğru parola
    resp_ok = client.post(
        "/api/auth/login",
        json={"email": student_user.email, "password": "Ogrenci12345!"},
    )
    assert resp_ok.status_code == 200
    data = resp_ok.json()
    assert "access_token" in data
    assert data["user"]["email"] == student_user.email
    # Cookie kontrolü
    assert "kutuphane_oturum" in resp_ok.cookies


def test_logout_revokes_token(client: TestClient, student_user: User) -> None:
    """Çıkış yapılan token ile bir daha korumalı endpoint'e erişilememesi."""
    login_resp = client.post(
        "/api/auth/login",
        json={"email": student_user.email, "password": "Ogrenci12345!"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # /api/auth/me başarılı olmalı
    me_resp = client.get("/api/auth/me", headers=headers)
    assert me_resp.status_code == 200

    # Çıkış yap
    logout_resp = client.post("/api/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

    # Tekrar me isteği yapılınca reddedilmeli
    me_resp_after = client.get("/api/auth/me", headers=headers)
    assert me_resp_after.status_code == 401
    assert me_resp_after.json()["error"]["code"] == "OTURUM_KAPATILDI"


def test_validation_errors_meaningful_turkish(client: TestClient) -> None:
    """Senaryo 15: Geçersiz veri gönderildiğinde anlamlı Türkçe doğrulama hatası dönmesi."""
    # Eksik alanlar, geçersiz e-posta, zayıf parola
    invalid_payload = {
        "student_number": "12",  # En az 5 haneli olmalı
        "full_name": "A",        # En az 3 karakter olmalı
        "email": "gecersiz-eposta",
        "password": "123",       # En az 8 karakter olmalı
    }
    response = client.post("/api/auth/register", json=invalid_payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "DOGRULAMA_HATASI"
    assert len(data["error"]["details"]) > 0
    fields = [d["field"] for d in data["error"]["details"]]
    assert "email" in fields
    assert "password" in fields
    assert "full_name" in fields
    assert "student_number" in fields
