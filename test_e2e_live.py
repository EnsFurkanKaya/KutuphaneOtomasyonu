import json
import random
import sys
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000"

def request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            err_json = json.loads(content)
        except Exception:
            err_json = {"raw": content}
        return e.code, err_json

print("="*60)
print("CANLI SİSTEM ENTEGRASYON DOĞRULAMA TESTİ (API + POSTGRESQL)")
print("="*60)

# 1. API Sağlık Kontrolü
code, res = request("/health")
print(f"\n[1] Sağlık Kontrolü: HTTP {code} -> {res}")
assert code == 200 and res.get("status") == "ok", "Sağlık kontrolü başarısız!"

# 2. Yönetici Girişi
print("\n[2] Yönetici Girişi Yapılıyor...")
code, res = request("/api/auth/login", method="POST", data={
    "email": "admin@kutuphane.edu.tr",
    "password": "Admin12345!"
})
print(f"    HTTP {code} - Admin Token Alındı.")
assert code == 200 and "access_token" in res, f"Admin girişi başarısız: {res}"
admin_token = res["access_token"]

# 3. Yeni Öğrenci Ekleme / Kayıt
rnd = random.randint(1000, 9999)
student_email = f"test.ogrenci.{rnd}@ogr.edu.tr"
student_number = f"2026{rnd}"
print(f"\n[3] Yeni Öğrenci Kaydediliyor ({student_email})...")
code, res = request("/api/auth/register", method="POST", data={
    "email": student_email,
    "student_number": student_number,
    "full_name": "Ahmet Yılmaz",
    "password": "Ogrenci12345!"
})
print(f"    HTTP {code} - Öğrenci ID: {res.get('id')}, Ad: {res.get('full_name')}")
assert code == 201, f"Öğrenci kaydı başarısız: {res}"

# 4. Yeni Öğrenci ile Giriş Yapma
print("\n[4] Yeni Öğrenci Giriş Yapıyor...")
code, res = request("/api/auth/login", method="POST", data={
    "email": student_email,
    "password": "Ogrenci12345!"
})
print(f"    HTTP {code} - Öğrenci Token Alındı.")
assert code == 200 and "access_token" in res, f"Öğrenci girişi başarısız: {res}"
student_token = res["access_token"]

# 5. Kategori Listesini Kontrol Et
print("\n[5] Kategori Kontrol Ediliyor...")
code, res = request("/api/categories", token=admin_token)
categories = res if isinstance(res, list) else res.get("items", [])
if not categories:
    code, cat_res = request("/api/categories", method="POST", data={
        "name": f"Test Kategorisi {rnd}",
        "description": "Otomasyon kategorisi"
    }, token=admin_token)
    category_id = cat_res["id"]
else:
    category_id = categories[0]["id"]
print(f"    Kategori ID: {category_id}")

# 6. Yönetici Kitap Ekliyor (Toplam: 2, Mevcut: 2)
isbn = f"978975{random.randint(1000000, 9999999)}"
book_payload = {
    "isbn": isbn,
    "title": f"Otomatik Test Kitabı {rnd}",
    "author": "Doğrulama Yazarı",
    "publisher": "Akademi Yayıncılık",
    "publication_year": 2024,
    "category_id": category_id,
    "shelf_location": "B-204",
    "total_copies": 2
}
print(f"\n[6] Yönetici Kitap Ekliyor (ISBN: {isbn}, Stok: 2)...")
code, res = request("/api/books", method="POST", data=book_payload, token=admin_token)
print(f"    HTTP {code} - Kitap ID: {res.get('id')}, Toplam: {res.get('total_copies')}, Mevcut: {res.get('available_copies')}")
assert code == 201, f"Kitap ekleme başarısız: {res}"
book_id = res["id"]
assert res["total_copies"] == 2 and res["available_copies"] == 2, "Başlangıç stoğu hatalı!"

# 7. Öğrenci Kitabı Ödünç Alıyor
print(f"\n[7] Öğrenci Kitabı Ödünç Alıyor (Kitap ID: {book_id})...")
code, res = request("/api/loans", method="POST", data={"book_id": book_id}, token=student_token)
print(f"    HTTP {code} - Ödünç Kayıt ID: {res.get('id')}, Durum: {res.get('status')}, Son İade: {res.get('due_at')}")
assert code == 201, f"Ödünç alma başarısız: {res}"
loan_id = res["id"]

# 8. Stok Düşüşünü Doğrulama (Toplam: 2, Mevcut: 1)
print("\n[8] Stok Kontrolü (Ödünç Sonrası)...")
code, res = request(f"/api/books/{book_id}", token=student_token)
print(f"    Toplam Kopya: {res['total_copies']}, Mevcut Kopya: {res['available_copies']}")
assert res["available_copies"] == 1, f"Mevcut stok 1 olmalıydı, bulunan: {res['available_copies']}"
print("    ✓ Stok doğru şekilde 2'den 1'e düştü.")

# 9. Aynı Kitabı İkinci Kez Ödünç Alma Denemesi (Kural 4: Mükerrer Ödünç Engeli)
print("\n[9] Aynı Kitabı İkinci Kez Ödünç Alma Denemesi...")
code, res = request("/api/loans", method="POST", data={"book_id": book_id}, token=student_token)
print(f"    HTTP {code} - Hata Kodu: {res.get('error', {}).get('code')}")
assert code == 409, f"Mükerrer ödünç engellenmeliydi (Beklenen 409, gelen {code})"
print("    ✓ Mükerrer ödünç başarıyla 409 Conflict ile engellendi.")

# 10. Kitap İade Etme
print(f"\n[10] Kitap İade Ediliyor (Ödünç ID: {loan_id})...")
code, res = request(f"/api/loans/{loan_id}/return", method="POST", token=student_token)
print(f"    HTTP {code} - Durum: {res.get('status')}, İade Tarihi: {res.get('returned_at')}")
assert code == 200 and res.get("status") == "RETURNED", f"İade işlemi başarısız: {res}"
print("    ✓ Kitap başarıyla iade edildi.")

# 11. Stok Artışını Doğrulama (Toplam: 2, Mevcut: 2)
print("\n[11] Stok Kontrolü (İade Sonrası)...")
code, res = request(f"/api/books/{book_id}", token=student_token)
print(f"    Toplam Kopya: {res['total_copies']}, Mevcut Kopya: {res['available_copies']}")
assert res["available_copies"] == 2, f"Mevcut stok 2 olmalıydı, bulunan: {res['available_copies']}"
print("    ✓ Stok doğru şekilde 1'den 2'ye yükseldi.")

# 12. Aynı Ödünç Kaydını İkinci Kez İade Etme Denemesi (Kural 8: Tekil İade)
print("\n[12] Aynı Kaydı İkinci Kez İade Etme Denemesi...")
code, res = request(f"/api/loans/{loan_id}/return", method="POST", token=student_token)
print(f"    HTTP {code} - Hata Kodu: {res.get('error', {}).get('code')}")
assert code == 409, f"Zaten iade edilmiş kayıt tekrar iade edilememeliydi (409 bekleniyordu, gelen: {code})"
print("    ✓ İkinci kez iade denemesi başarıyla 409 Conflict ile engellendi.")

print("\n" + "="*60)
print("SONUÇ: KİTAP EKLEME, ÖĞRENCİ EKLEME, ÖDÜNÇ VERME, İADE VE")
print("STOK HESAPLAMA İŞLEVLERİNİN TÜMÜ %100 DOĞRULANDI VE ÇALIŞIYOR!")
print("="*60)
