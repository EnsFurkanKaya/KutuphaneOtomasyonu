"""Veritabanı örnek veri yükleme (seed) betiği.

Geliştirme ve test ortamları için yönetici, öğrenciler, kategoriler,
kitaplar ve örnek ödünç/gecikmiş kayıtları oluşturur. Tekrar çalıştırıldığında
verileri mükerrer oluşturmaz (idempotent).
"""
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.domain.enums import Role
from app.models.book import Book
from app.models.category import Category
from app.models.loan import Loan
from app.models.user import User


def seed_data(db: Session) -> None:
    settings = get_settings()
    now = datetime.now(timezone.utc)

    # 1. KATEGORİLER
    categories_data = [
        {"name": "Bilgisayar & Yazılım", "description": "Yazılım mühendisliği, algoritmalar, programlama dilleri ve sistem tasarımı kitapları."},
        {"name": "Edebiyat & Roman", "description": "Klasik ve çağdaş dünya edebiyatı ve Türk edebiyatı eserleri."},
        {"name": "Tarih & Araştırma", "description": "Dünya tarihi, Osmanlı tarihi ve yakın dönem araştırmaları."},
        {"name": "Fen & Matematik", "description": "Fizik, matematik, analiz ve doğa bilimleri başvuru kaynakları."},
        {"name": "Felsefe & Sosyoloji", "description": "Düşünce tarihi, mantık, ahlak felsefesi ve toplum bilimleri."},
    ]

    categories_map: dict[str, Category] = {}
    for cat_data in categories_data:
        cat = db.execute(select(Category).where(Category.name == cat_data["name"])).scalar_one_or_none()
        if not cat:
            cat = Category(name=cat_data["name"], description=cat_data["description"], is_active=True)
            db.add(cat)
            db.flush()
        categories_map[cat.name] = cat

    # 2. KULLANICILAR (Yönetici ve Öğrenciler)
    # Yerel geliştirme için yönetici parolası ortam değişkeninden alınır ya da varsayılan kullanılır
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin12345!")
    student_password = os.getenv("SEED_STUDENT_PASSWORD", "Ogrenci12345!")

    # Yönetici
    admin = db.execute(select(User).where(User.email == "admin@kutuphane.edu.tr")).scalar_one_or_none()
    if not admin:
        admin = User(
            student_number=None,
            full_name="Kütüphane Sistem Yöneticisi",
            email="admin@kutuphane.edu.tr",
            password_hash=hash_password(admin_password),
            role=Role.ADMIN.value,
            is_active=True,
            must_change_password=os.getenv("APP_ENV") == "production",
        )
        db.add(admin)
        db.flush()

    # Öğrenciler
    students_data = [
        {"student_number": "2026001", "full_name": "Ahmet Yılmaz", "email": "ahmet.yilmaz@ogr.edu.tr"},
        {"student_number": "2026002", "full_name": "Ayşe Kaya", "email": "ayse.kaya@ogr.edu.tr"},
        {"student_number": "2026003", "full_name": "Mehmet Demir", "email": "mehmet.demir@ogr.edu.tr"},
        {"student_number": "2026004", "full_name": "Zeynep Çelik", "email": "zeynep.celik@ogr.edu.tr"},
        {"student_number": "2026005", "full_name": "Burak Öztürk", "email": "burak.ozturk@ogr.edu.tr"},
    ]

    students_map: dict[str, User] = {}
    for s_data in students_data:
        stu = db.execute(select(User).where(User.email == s_data["email"])).scalar_one_or_none()
        if not stu:
            stu = User(
                student_number=s_data["student_number"],
                full_name=s_data["full_name"],
                email=s_data["email"],
                password_hash=hash_password(student_password),
                role=Role.STUDENT.value,
                is_active=True,
                must_change_password=False,
            )
            db.add(stu)
            db.flush()
        students_map[stu.student_number] = stu

    # 3. KİTAPLAR
    books_data = [
        {
            "isbn": "9780000000001",
            "title": "Nesne Yönelimli Programlama",
            "author": "Mehmet Demir",
            "publisher": "Akademi Yayınları",
            "publication_year": 2023,
            "category_name": "Bilgisayar & Yazılım",
            "shelf_location": "A-101",
            "total_copies": 5,
            "available_copies": 4,  # Ahmet Yılmaz 1 tane aktif ödünç alacak
            "description": "Nesne yönelimli yazılım tasarımı prensipleri, UML modelleme ve pratik desenler.",
        },
        {
            "isbn": "9780000000002",
            "title": "Veritabanı Yönetim Sistemleri",
            "author": "Cemil Güler",
            "publisher": "Teknik Basım",
            "publication_year": 2022,
            "category_name": "Bilgisayar & Yazılım",
            "shelf_location": "A-102",
            "total_copies": 4,
            "available_copies": 3,
            "description": "İlişkisel veritabanı tasarımı, normalizasyon, SQL sorgulama ve ACID kuralları.",
        },
        {
            "isbn": "9780000000003",
            "title": "Temiz Kod: Çevik Yazılım Sanatı",
            "author": "Robert C. Martin",
            "publisher": "Nobel Yayın",
            "publication_year": 2020,
            "category_name": "Bilgisayar & Yazılım",
            "shelf_location": "A-103",
            "total_copies": 3,
            "available_copies": 2,  # 1 tane gecikmiş ödünç olacak
            "description": "Sürdürülebilir, okunabilir ve test edilebilir yazılım geliştirme rehberi.",
        },
        {
            "isbn": "9780000000004",
            "title": "Algoritmalar ve Veri Yapıları",
            "author": "Thomas H. Cormen",
            "publisher": "Akademik Çeviri",
            "publication_year": 2021,
            "category_name": "Bilgisayar & Yazılım",
            "shelf_location": "A-104",
            "total_copies": 2,
            "available_copies": 2,
            "description": "Temel ve ileri düzey arama, sıralama ve grafik algoritmaları.",
        },
        {
            "isbn": "9780000000005",
            "title": "Kürk Mantolu Madonna",
            "author": "Sabahattin Ali",
            "publisher": "YKY",
            "publication_year": 2019,
            "category_name": "Edebiyat & Roman",
            "shelf_location": "B-201",
            "total_copies": 6,
            "available_copies": 5,
            "description": "Raif Efendi ve Maria Puder'in unutulmaz ve dokunaklı aşk hikayesi.",
        },
        {
            "isbn": "9780000000006",
            "title": "Suç ve Ceza",
            "author": "Fyodor Dostoyevski",
            "publisher": "İletişim Yayınları",
            "publication_year": 2018,
            "category_name": "Edebiyat & Roman",
            "shelf_location": "B-202",
            "total_copies": 4,
            "available_copies": 4,
            "description": "Raskolnikov'un ahlaki çatışması, vicdan muhasebesi ve kefaret arayışı.",
        },
        {
            "isbn": "9780000000007",
            "title": "Saatleri Ayarlama Enstitüsü",
            "author": "Ahmet Hamdi Tanpınar",
            "publisher": "Dergâh Yayınları",
            "publication_year": 2017,
            "category_name": "Edebiyat & Roman",
            "shelf_location": "B-203",
            "total_copies": 3,
            "available_copies": 3,
            "description": "Doğu ile Batı arasında bocalayan modernleşme sürecimizin hiciv dolu şaheseri.",
        },
        {
            "isbn": "9780000000008",
            "title": "Kısa Dünya Tarihi",
            "author": "Ernst Gombrich",
            "publisher": "İnkılap",
            "publication_year": 2021,
            "category_name": "Tarih & Araştırma",
            "shelf_location": "C-301",
            "total_copies": 3,
            "available_copies": 3,
            "description": "İnsanlığın ilk ateş yakışından modern çağa kadar uzanan akıcı tarihi serüveni.",
        },
        {
            "isbn": "9780000000009",
            "title": "Osmanlı İmparatorluğu: Klasik Çağ",
            "author": "Halil İnalcık",
            "publisher": "Kronik Kitap",
            "publication_year": 2020,
            "category_name": "Tarih & Araştırma",
            "shelf_location": "C-302",
            "total_copies": 4,
            "available_copies": 4,
            "description": "Tarihçilerin kutbu Halil İnalcık'tan Osmanlı devlet ve toplum yapısı.",
        },
        {
            "isbn": "9780000000010",
            "title": "Devlet",
            "author": "Platon",
            "publisher": "Türkiye İş Bankası",
            "publication_year": 2019,
            "category_name": "Felsefe & Sosyoloji",
            "shelf_location": "D-401",
            "total_copies": 5,
            "available_copies": 5,
            "description": "İdeal toplum, adalet, yöneticilerin erdemleri ve felsefi mağara alegorisi.",
        },
    ]

    books_map: dict[str, Book] = {}
    for b_data in books_data:
        bk = db.execute(select(Book).where(Book.isbn == b_data["isbn"])).scalar_one_or_none()
        cat = categories_map.get(b_data["category_name"])
        if not bk:
            bk = Book(
                isbn=b_data["isbn"],
                title=b_data["title"],
                author=b_data["author"],
                publisher=b_data["publisher"],
                publication_year=b_data["publication_year"],
                category_id=cat.id if cat else None,
                shelf_location=b_data["shelf_location"],
                total_copies=b_data["total_copies"],
                available_copies=b_data["available_copies"],
                description=b_data["description"],
                is_active=True,
            )
            db.add(bk)
            db.flush()
        books_map[bk.isbn] = bk

    # 4. ÖDÜNÇ VE İADE SENARYOLARI (Object diagram ve rapor senaryoları)
    # Senaryo 1: Ahmet Yılmaz (2026001) -> Nesne Yönelimli Programlama (9780000000001) aktif ödünç
    # (Ödünç: 2026-10-10, Son İade: 2026-10-24, İade: None)
    ahmet = students_map.get("2026001")
    nyp_book = books_map.get("9780000000001")
    if ahmet and nyp_book:
        existing_loan1 = db.execute(
            select(Loan).where(Loan.user_id == ahmet.id, Loan.book_id == nyp_book.id, Loan.returned_at.is_(None))
        ).scalar_one_or_none()
        if not existing_loan1:
            loan1 = Loan(
                user_id=ahmet.id,
                book_id=nyp_book.id,
                borrowed_at=datetime(2026, 10, 10, 10, 0, tzinfo=timezone.utc),
                due_at=datetime(2026, 10, 24, 10, 0, tzinfo=timezone.utc),
                returned_at=None,
            )
            db.add(loan1)

    # Senaryo 2: Ayşe Kaya (2026002) -> Temiz Kod (9780000000003) Gecikmiş Ödünç
    # (Ödünç: 20 gün önce, Son İade: 6 gün önce, İade: None -> Gecikme raporunda yer almalı)
    ayse = students_map.get("2026002")
    clean_code = books_map.get("9780000000003")
    if ayse and clean_code:
        existing_loan2 = db.execute(
            select(Loan).where(Loan.user_id == ayse.id, Loan.book_id == clean_code.id, Loan.returned_at.is_(None))
        ).scalar_one_or_none()
        if not existing_loan2:
            borrowed_past = now - timedelta(days=20)
            due_past = now - timedelta(days=6)
            loan2 = Loan(
                user_id=ayse.id,
                book_id=clean_code.id,
                borrowed_at=borrowed_past,
                due_at=due_past,
                returned_at=None,
            )
            db.add(loan2)

    # Senaryo 3: Mehmet Demir (2026003) -> Veritabanı Sistemleri (9780000000002) Aktif Ödünç
    mehmet = students_map.get("2026003")
    db_book = books_map.get("9780000000002")
    if mehmet and db_book:
        existing_loan3 = db.execute(
            select(Loan).where(Loan.user_id == mehmet.id, Loan.book_id == db_book.id, Loan.returned_at.is_(None))
        ).scalar_one_or_none()
        if not existing_loan3:
            loan3 = Loan(
                user_id=mehmet.id,
                book_id=db_book.id,
                borrowed_at=now - timedelta(days=5),
                due_at=now + timedelta(days=9),
                returned_at=None,
            )
            db.add(loan3)

    # Senaryo 4: Zeynep Çelik (2026004) -> Kürk Mantolu Madonna (9780000000005) Başarıyla İade Edilmiş
    zeynep = students_map.get("2026004")
    madonna = books_map.get("9780000000005")
    if zeynep and madonna:
        existing_loan4 = db.execute(
            select(Loan).where(Loan.user_id == zeynep.id, Loan.book_id == madonna.id, Loan.returned_at.is_not(None))
        ).scalar_one_or_none()
        if not existing_loan4:
            b_at = now - timedelta(days=25)
            d_at = now - timedelta(days=11)
            r_at = now - timedelta(days=12)  # Zamanında iade edildi
            loan4 = Loan(
                user_id=zeynep.id,
                book_id=madonna.id,
                borrowed_at=b_at,
                due_at=d_at,
                returned_at=r_at,
            )
            db.add(loan4)

    db.commit()
    print("Örnek veriler başarıyla yüklendi.")


def init_db_and_seed() -> None:
    """Tabloları doğrudan oluşturur ve seed verilerini yükler."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_data(session)


if __name__ == "__main__":
    init_db_and_seed()
