# Online Kütüphane Yönetim Sistemi

Üniversite kütüphaneleri için geliştirilmiş, rol tabanlı yetkilendirme, gerçek zamanlı stok takibi, ödünç/iade iş akışları, otomatik gecikme cezası hesaplama ve zengin raporlama özelliklerine sahip modern ve güvenli full-stack web uygulaması.

---

##  İçindekiler
1. [Mimarî ve Teknolojiler](#-mimarî-ve-teknolojiler)
2. [Klasör Yapısı](#-klasör-yapısı)
3. [Varsayılan Kullanıcı Hesapları](#-varsayılan-kullanıcı-hesapları)
4. [Hızlı Başlangıç (Docker Compose)](#-hızlı-başlangıç-docker-compose)
5. [Yerel Geliştirme Ortamı Kurulumu](#-yerel-geliştirme-ortamı-kurulumu)
6. [API Uç Noktaları ve Swagger](#-api-uç-noktaları-ve-swagger)
7. [İş Kuralları ve Doğrulamalar](#-iş-kuralları-ve-doğrulamalar)
8. [UML Diyagramları](#-uml-diyagramları)
9. [Otomatik Testler](#-otomatik-testler)

---

##  Mimarî ve Teknolojiler

Uygulama 3 temel katmandan oluşan katmanlı mimariye (Clean/Layered Architecture) sahiptir:
1. **Frontend (İstemci Katmanı):** React 18, TypeScript, Tailwind CSS, Lucide Icons, Vite
2. **Backend (API & İş Mantığı Katmanı):** Python 3.12+, FastAPI, SQLAlchemy ORM, Pydantic v2, Alembic
3. **Veritabanı Katmanı:** PostgreSQL 16 (İlişkisel bütünlük, foreign key'ler, index'ler ve check kısıtları)

### Temel Güvenlik ve Altyapı
- **Kimlik Doğrulama:** JWT (JSON Web Token) tabanlı Access Token ve token iptal (revocation / blacklist) mekanizması
- **Parola Güvenliği:** Passlib ile Argon2 / Bcrypt hash algoritması
- **Eşzamanlılık (Concurrency) Koruması:** Ödünç alma işlemlerinde stok yarış durumlarını (race condition) engellemek için veritabanı seviyesinde `SELECT ... FOR UPDATE` kilit mekanizması
- **Konteynerizasyon:** Çok aşamalı (multi-stage) Dockerfile yapılandırmaları ve tek tıkla ayağa kaldıran Docker Compose

---

##  Klasör Yapısı

```
KütüphaneSistemi/
├── PROMPT.md                  # Projenin orijinal ister ve şartname belgesi
├── README.md                  # Proje kurulum ve kullanım dokümantasyonu
├── docker-compose.yml         # PostgreSQL, Backend API ve Frontend servisleri
├── .env.example               # Örnek çevre değişkenleri şablonu
├── .gitignore                 # Versiyon kontrol yoksayma kuralları
│
├── uml/                       # PlantUML kaynak dosyaları
│   ├── class-diagram.puml     # UML Sınıf Diyagramı
│   ├── object-diagram.puml    # UML Nesne Diyagramı
│   ├── package-diagram.puml   # UML Paket Diyagramı
│   └── deployment-diagram.puml# UML Dağıtım Diyagramı
│
├── backend/                   # Python FastAPI REST API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── main.py            # FastAPI uygulama girişi ve CORS ayarları
│   │   ├── core/              # Konfigürasyon, güvenlik ve JWT işlemleri
│   │   ├── db/                # Oturum yönetimi, Base model ve seed verileri
│   │   ├── domain/            # Çerçeveden bağımsız temel iş kuralları (Rules)
│   │   ├── models/            # SQLAlchemy veritabanı tabloları (User, Book, Category, Loan)
│   │   ├── schemas/           # Pydantic DTO ve doğrulama şemaları
│   │   ├── repositories/      # Veri erişim katmanı (Repository Pattern)
│   │   ├── services/          # Uygulama iş akışları ve transaction yönetimi
│   │   └── api/               # REST API yönlendiricileri ve hata yakalayıcılar
│   └── tests/                 # pytest test suiteleri (Birim, entegrasyon, yarış durumu testleri)
│
└── frontend/                  # React & TypeScript İstemci
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    └── src/
        ├── components/        # Yeniden kullanılabilir arayüz bileşenleri (Navbar, Sidebar vb.)
        ├── contexts/          # Kimlik doğrulama state yönetimi (AuthContext)
        ├── layouts/           # Sayfa yerleşimleri (MainLayout)
        ├── pages/             # Öğrenci ve Yönetici sayfaları, gösterge panelleri
        ├── services/          # Axios tabanlı REST API istemcisi
        ├── types/             # TypeScript tip tanımları
        └── utils/             # Tarih, para ve metin biçimlendiricileri
```

---

## Varsayılan Kullanıcı Hesapları

Veritabanı otomatik olarak tohumlandığında (seed) aşağıdaki test kullanıcıları hazır gelir:

| Rol | E-Posta | Şifre | Açıklama |
|---|---|---|---|
| **Yönetici (Admin)** | `admin@kutuphane.edu.tr` | `Admin12345!` | Tüm kitap, kategori, kullanıcı ve ödünçleri yönetebilir |
| **Öğrenci 1** | `ogrenci@kutuphane.edu.tr` | `Ogrenci12345!` | Standart öğrenci hesabı (Aktif ödünçleri mevcut) |
| **Öğrenci 2** | `ayse.yilmaz@ogr.edu.tr` | `Ogrenci12345!` | 3 kitap ödünç limitine ulaşmış öğrenci (Limit testi) |
| **Öğrenci 3** | `mehmet.kaya@ogr.edu.tr` | `Ogrenci12345!` | Gecikmiş ödüncü olan öğrenci (Gecikme cezası ve engelleme testi) |

---

##  Hızlı Başlangıç (Docker Compose)

Sistemi tüm bileşenleriyle (PostgreSQL, Backend API, Frontend) tek komutla çalıştırmak için:

```bash
# 1. Proje ana dizininde çevre değişkeni dosyasını oluşturun:
cp .env.example .env

# 2. Tüm servisleri derleyin ve arka planda ayağa kaldırın:
docker compose up -d --build
```

Servisler hazır olduğunda:
- **Frontend Arayüzü:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Dokümantasyonu:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

##  Yerel Geliştirme Ortamı Kurulumu

Eğer Docker kullanmadan doğrudan yerel ortamda çalıştırmak isterseniz:

### 1. Veritabanı (PostgreSQL)
PostgreSQL üzerinde `kutuphane_db` adında bir veritabanı oluşturun ve `.env` dosyasındaki `DATABASE_URL` bağlantı adresini güncelleyin.

### 2. Backend Kurulumu
```bash
cd backend

# Python sanal ortamı oluşturun ve aktifleştirin
python -m venv venv
# Windows için:
.\venv\Scripts\activate
# Linux/macOS için:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt -r requirements-dev.txt

# Veritabanı tablolarını ve seed verilerini yükleyin
python -m app.db.seed

# API sunucusunu başlatın
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Kurulumu
```bash
cd frontend

# Bağımlılıkları yükleyin
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```
Frontend geliştirme sunucusu [http://localhost:5173](http://localhost:5173) adresinde çalışacaktır.

---

##  API Uç Noktaları ve Swagger

Tüm uç noktalar Türkçe açıklamalar ve standart JSON yanıt formatıyla dokümante edilmiştir:

### Kimlik Doğrulama (`/api/v1/auth`)
- `POST /register`: Öğrenci kayıt işlemi
- `POST /login`: Giriş yapma ve JWT Access Token alma
- `POST /logout`: Çıkış yapma ve aktif token'ı kara listeye alma
- `GET /me`: Oturum açmış kullanıcının profil bilgilerini getirme

### Kitap Yönetimi (`/api/v1/books`)
- `GET /`: Kitapları listeleme (arama, kategori filtresi, sayfalama)
- `GET /{id}`: Kitap detayı
- `POST /`: Yeni kitap ekleme *(Yönetici)*
- `PUT /{id}`: Kitap güncelleme *(Yönetici)*
- `DELETE /{id}`: Kitap silme (ödünçte kitap varsa engellenir) *(Yönetici)*

### Kategori Yönetimi (`/api/v1/categories`)
- `GET /`: Kategorileri listeleme
- `POST /`: Yeni kategori oluşturma *(Yönetici)*
- `PUT /{id}`: Kategori güncelleme *(Yönetici)*
- `DELETE /{id}`: Kategori silme *(Yönetici)*

### Ödünç ve İade İşlemleri (`/api/v1/loans`)
- `POST /borrow`: Kitap ödünç alma (iş kuralları ve stok kilit kontrolü)
- `POST /{id}/return`: Kitap iade etme (gecikme cezası hesaplama)
- `GET /my`: Giriş yapan öğrencinin ödünç geçmişi ve aktif kitapları
- `GET /`: Tüm ödünç kayıtlarını filtreleme ve arama *(Yönetici)*

### Raporlama (`/api/v1/reports`) *(Yönetici)*
- `GET /summary`: Toplam kitap, aktif ödünç, gecikmiş iade ve üye sayıları
- `GET /overdue`: Gecikmiş kitaplar ve hesaplanan ceza tutarları
- `GET /popular-books`: En çok ödünç alınan popüler kitaplar

---

##  İş Kuralları ve Doğrulamalar

1. **Ödünç Limiti:** Bir öğrenci aynı anda en fazla **3 aktif** kitaba sahip olabilir.
2. **Ödünç Süresi:** Standart ödünç süresi **15 gündür**.
3. **Gecikme Engeli:** Teslim tarihi geçmiş ve iade edilmemiş kitabı bulunan bir öğrenci yeni kitap ödünç alamaz.
4. **Mükerrer Ödünç Kısıtı:** Bir öğrenci şu anda elinde bulunan aynı kitabı tekrar ödünç alamaz.
5. **Stok Güvencesi:** Yalnızca `mevcut_adet > 0` olan kitaplar ödünç verilebilir. Ödünç işleminde mevcut adet 1 azaltılır, iade edildiğinde 1 artırılır. Toplam adet ise fiziksel envanteri temsil eder.
6. **Ceza Hesabı:** Geciken her gün için sistem `günlük_ceza_tutari * gecikme_gun_sayisi` formülü ile ceza hesaplar.

---

##  UML Diyagramları

Projenin `uml/` klasörü altında 4 adet eksiksiz ve standart PlantUML diyagramı yer almaktadır:

1. **`class-diagram.puml`:** Sınıf diyagramı (User, Book, Category, Loan varlıkları, nitelikleri, metotları ve aralarındaki bire-çok ilişkiler).
2. **`object-diagram.puml`:** Nesne diyagramı (Belirli bir çalışma anında somut nesne örnekleri, attribute değerleri ve nesne bağlantıları).
3. **`package-diagram.puml`:** Paket diyagramı (Presentation, Application, Domain, Infrastructure, Persistence katman bağımlılıkları).
4. **`deployment-diagram.puml`:** Dağıtım diyagramı (Client Device, Web Server [Nginx], API Server [Uvicorn/FastAPI] ve Database Server [PostgreSQL] donanım düğümleri ve protokoller).

---

##  Otomatik Testler

Backend testleri `pytest` kullanılarak yazılmıştır:
```bash
cd backend
pytest -v
```

### Kapsanan Test Senaryoları
- **`test_rules.py`:** Saf iş kuralları (limit, gecikme, stok ve ceza formülleri)
- **`test_auth.py`:** Kayıt, giriş, hatalı şifre, token geçerliliği ve yetkisiz erişim kontrolleri
- **`test_books.py`:** Kitap CRUD işlemleri, arama ve kategori filtreleri
- **`test_loans.py`:** Ödünç alma, iade etme, 3 kitap sınırı, gecikme engeli ve stok değişimleri
- **`test_concurrency.py`:** Son 1 adet kalan kitap için eşzamanlı ödünç alma yarış durumu testi (Race Condition)
- **`test_reports.py`:** Dashboard özet verileri ve gecikmiş ödünç raporları
