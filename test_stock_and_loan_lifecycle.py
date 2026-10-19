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

print("=" * 70)
print("ÖZEL STOK VE ÖDÜNÇ/İADE DÖNGÜSÜ DOĞRULAMA TESTİ")
print("1. Stokta olmayan kitabın ödünç verilememesi (0 stok engeli)")
print("2. İade edilen kitabın anında stoğa geri eklenmesi (+1 stok)")
print("=" * 70)

# ADIM 1: Yönetici Girişi
print("\n[ADIM 1] Yönetici oturumu açılıyor...")
code, admin_res = request("/api/auth/login", method="POST", data={
    "email": "admin@kutuphane.edu.tr",
    "password": "Admin12345!"
})
assert code == 200, f"Yönetici girişi başarısız: {admin_res}"
admin_token = admin_res["access_token"]
print("  ✓ Yönetici girişi başarılı.")

# ADIM 2: İki Farklı Öğrenci Hesabı Oluşturma (Öğrenci A ve Öğrenci B)
rnd = random.randint(10000, 99999)

print("\n[ADIM 2] İki farklı öğrenci hesabı oluşturuluyor...")
# Öğrenci A
email_a = f"ogrenci.a.{rnd}@ogr.edu.tr"
num_a = f"2026{rnd}1"
code, res_a = request("/api/auth/register", method="POST", data={
    "email": email_a,
    "student_number": num_a,
    "full_name": f"Öğrenci A ({rnd})",
    "password": "Ogrenci12345!"
})
assert code == 201, f"Öğrenci A kaydı başarısız: {res_a}"
code, login_a = request("/api/auth/login", method="POST", data={"email": email_a, "password": "Ogrenci12345!"})
token_a = login_a["access_token"]
print(f"  ✓ Öğrenci A oluşturuldu ve giriş yaptı (ID: {res_a['id']}, E-posta: {email_a})")

# Öğrenci B
email_b = f"ogrenci.b.{rnd}@ogr.edu.tr"
num_b = f"2026{rnd}2"
code, res_b = request("/api/auth/register", method="POST", data={
    "email": email_b,
    "student_number": num_b,
    "full_name": f"Öğrenci B ({rnd})",
    "password": "Ogrenci12345!"
})
assert code == 201, f"Öğrenci B kaydı başarısız: {res_b}"
code, login_b = request("/api/auth/login", method="POST", data={"email": email_b, "password": "Ogrenci12345!"})
token_b = login_b["access_token"]
print(f"  ✓ Öğrenci B oluşturuldu ve giriş yaptı (ID: {res_b['id']}, E-posta: {email_b})")

# ADIM 3: Kategoriyi belirleme veya oluşturma
code, cat_res = request("/api/categories", token=admin_token)
categories = cat_res if isinstance(cat_res, list) else cat_res.get("items", [])
category_id = categories[0]["id"] if categories else 1

# ADIM 4: Yalnızca 1 Adet Kopyası Olan Özel Bir Kitap Ekleme
isbn = f"978975{random.randint(1000000, 9999999)}"
book_title = f"Tek Nüsha Nadir Eser #{rnd}"
print(f"\n[ADIM 4] Yalnızca 1 Adet Kopyası Olan Kitap Ekleniyor...")
print(f"  Kitap: '{book_title}' | ISBN: {isbn}")
code, book_res = request("/api/books", method="POST", data={
    "isbn": isbn,
    "title": book_title,
    "author": "Özel Test Yazarı",
    "category_id": category_id,
    "total_copies": 1,
    "shelf_location": "OZEL-01"
}, token=admin_token)
assert code == 201, f"Kitap ekleme başarısız: {book_res}"
book_id = book_res["id"]
print(f"  ✓ Kitap oluşturuldu (ID: {book_id})")
print(f"    -> Toplam Kopya: {book_res['total_copies']}")
print(f"    -> Mevcut (Raftaki) Kopya: {book_res['available_copies']}")
assert book_res["total_copies"] == 1 and book_res["available_copies"] == 1, "Başlangıç stok durumu hatalı!"

# ADIM 5: Öğrenci A Kitabı Ödünç Alıyor
print(f"\n[ADIM 5] Öğrenci A tek kopyayı ödünç alıyor...")
code, loan_res = request("/api/loans", method="POST", data={"book_id": book_id}, token=token_a)
assert code == 201, f"Ödünç alma başarısız: {loan_res}"
loan_id = loan_res["id"]
print(f"  ✓ Ödünç alma başarılı (Ödünç ID: {loan_id}, Durum: {loan_res['status']})")

# ADIM 6: Ödünç Sonrası Stok Doğrulaması (1 -> 0)
print("\n[ADIM 6] Stok kontrol ediliyor (Öğrenci A ödünç aldıktan sonra)...")
code, book_check_1 = request(f"/api/books/{book_id}", token=token_a)
print(f"    -> Toplam Kopya: {book_check_1['total_copies']}")
print(f"    -> Mevcut Kopya : {book_check_1['available_copies']}")
assert book_check_1["total_copies"] == 1, "Toplam kopya değişmemeli!"
assert book_check_1["available_copies"] == 0, f"Mevcut kopya 0 olmalıydı! Bulunan: {book_check_1['available_copies']}"
print("  ✓ DOĞRULANDI: Kitabın mevcut kopyası başarıyla 0'a düştü.")

# ADIM 7: KRİTİK TEST 1 - Stokta Olmayan Kitabı Öğrenci B'nin Ödünç Alma Girişimi
print("\n[ADIM 7] KRİTİK KONTROL 1: Stokta olmayan (0 kopya) kitabı Öğrenci B ödünç almaya çalışıyor...")
code, reject_res = request("/api/loans", method="POST", data={"book_id": book_id}, token=token_b)
print(f"    HTTP Yanıt Kodu: {code} (Beklenen: 400 Bad Request)")
print(f"    Hata Detayı    : {reject_res.get('error')}")
assert code == 400, f"Stokta olmayan kitap ödünç verilmemeliydi! Gelen HTTP kodu: {code}"
assert reject_res.get("error", {}).get("code") in ("STOK_YOK", "IS_KURALI_IHLALI"), "Beklenen hata kodu dönmedi!"
assert "kopyası yok" in reject_res.get("error", {}).get("message", ""), "Hata mesajı stok yetersizliğini belirtmeli!"
print("  ✓ BAŞARILI: Sistem stok yetersizliği nedeniyle ödünç işlemini kesin olarak REDDETTİ.")

# ADIM 8: Reddedilme Sonrası Stok Bozulmadı Kontrolü (Stok asla -1 olamaz)
print("\n[ADIM 8] Stok kontrolü (Başarısız ödünç denemesinden sonra)...")
code, book_check_2 = request(f"/api/books/{book_id}", token=token_b)
print(f"    -> Toplam Kopya: {book_check_2['total_copies']}")
print(f"    -> Mevcut Kopya : {book_check_2['available_copies']}")
assert book_check_2["available_copies"] == 0, "Mevcut kopya negatif veya farklı bir değere bozulmuş!"
print("  ✓ DOĞRULANDI: Başarısız işlem sonrası stok asla negatif olmadı, tam olarak 0 kaldı.")

# ADIM 9: KRİTİK TEST 2 - Öğrenci A Kitabı İade Ediyor ve Stoğa Geri Ekleniyor
print(f"\n[ADIM 9] KRİTİK KONTROL 2: Öğrenci A kitabı iade ediyor (Ödünç ID: {loan_id})...")
code, return_res = request(f"/api/loans/{loan_id}/return", method="POST", token=token_a)
assert code == 200, f"İade işlemi başarısız: {return_res}"
assert return_res["status"] == "RETURNED", "Ödünç durumu RETURNED olmalı!"
assert return_res["returned_at"] is not None, "İade tarihi atanmalı!"
print(f"  ✓ İade işlemi onaylandı. İade Tarihi: {return_res['returned_at']}")

# ADIM 10: İade Sonrası Stok Artışı Kontrolü (0 -> 1)
print("\n[ADIM 10] İade sonrası stok kontrolü (Stoğa geri eklenme doğrulaması)...")
code, book_check_3 = request(f"/api/books/{book_id}", token=token_a)
print(f"    -> Toplam Kopya: {book_check_3['total_copies']}")
print(f"    -> Mevcut Kopya : {book_check_3['available_copies']}")
assert book_check_3["total_copies"] == 1, "Toplam kopya değişmemeli!"
assert book_check_3["available_copies"] == 1, f"İade edilen kitap stoğa dönmeli ve 1 olmalıydı! Bulunan: {book_check_3['available_copies']}"
print("  ✓ DOĞRULANDI: İade edilen kitap tam zamanında STOĞA GERİ EKLENDİ (Mevcut kopya 1 oldu).")

# ADIM 11: Öğrenci B Şimdi Kitabı Ödünç Alabiliyor
print("\n[ADIM 11] Öğrenci B artık stokta olan (1 kopya) kitabı tekrar ödünç almayı deniyor...")
code, loan_b_res = request("/api/loans", method="POST", data={"book_id": book_id}, token=token_b)
assert code == 201, f"Öğrenci B ödünç alabilmeliydi: {loan_b_res}"
loan_b_id = loan_b_res["id"]
print(f"  ✓ BAŞARILI: Öğrenci B kitabı başarıyla ödünç alabildi (Ödünç ID: {loan_b_id}).")

# ADIM 12: İkinci Ödünç Sonrası Tekrar 0'a Düşme ve İade İle Tekrar 1'e Çıkma
print("\n[ADIM 12] Tam döngü: Öğrenci B iade ediyor ve stok tekrar 1'e dönüyor...")
code, book_check_4 = request(f"/api/books/{book_id}", token=token_b)
assert book_check_4["available_copies"] == 0, "Ödünç sonrası stok 0 olmalı!"

code, return_b_res = request(f"/api/loans/{loan_b_id}/return", method="POST", token=token_b)
assert code == 200, "İkinci iade başarılı olmalı!"

code, book_check_final = request(f"/api/books/{book_id}", token=token_b)
assert book_check_final["available_copies"] == 1, "Son stok 1 olmalı!"
print(f"    -> Nihai Toplam Kopya: {book_check_final['total_copies']}")
print(f"    -> Nihai Mevcut Kopya : {book_check_final['available_copies']}")
print("  ✓ DOĞRULANDI: İkinci ödünç-iade döngüsünde de stok %100 tutarlı kaldı.")

print("\n" + "=" * 70)
print("TEST SONUCU: TÜM KRİTİK KONTROLLER BAŞARIYLA GEÇTİ!")
print("1. Stokta olmayan kitap KESİNLİKLE ödünç verilemiyor (0 stok kuralı).")
print("2. İade edilen kitap ANINDA ve TAM OLARAK stoğa geri ekleniyor.")
print("3. Stok hiçbir aşamada negatif olmuyor ve fiziksel envanteri aşmıyor.")
print("=" * 70)
