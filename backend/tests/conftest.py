"""Pytest test yapılandırması ve fixture'ları."""
import os
import pytest
from collections.abc import Iterator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Test ortamı ayarları
os.environ["APP_ENV"] = "test"
os.environ["SECRET_KEY"] = "test-gizli-anahtari-en-az-32-karakter-uzunlugunda-olmali"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.core.config import get_settings
# Settings cache'ini temizle
get_settings.cache_clear()

import app.models  # Tüm modelleri Base.metadata içine kaydeder
from app.db.base import Base
from app.db.session import get_db
from app.domain.enums import Role
from app.main import app
from app.models.book import Book
from app.models.category import Category
from app.models.user import User
from app.core.security import hash_password, create_access_token

# SQLite test motoru
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database() -> Iterator[None]:
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session() -> Iterator[Session]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session: Session) -> User:
    admin = User(
        email="admin@test.edu.tr",
        full_name="Test Yöneticisi",
        password_hash=hash_password("Admin12345!"),
        role=Role.ADMIN.value,
        is_active=True,
        must_change_password=False,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def student_user(db_session: Session) -> User:
    student = User(
        student_number="2026101",
        email="ogrenci1@test.edu.tr",
        full_name="Birinci Öğrenci",
        password_hash=hash_password("Ogrenci12345!"),
        role=Role.STUDENT.value,
        is_active=True,
        must_change_password=False,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def student_user_2(db_session: Session) -> User:
    student2 = User(
        student_number="2026102",
        email="ogrenci2@test.edu.tr",
        full_name="İkinci Öğrenci",
        password_hash=hash_password("Ogrenci12345!"),
        role=Role.STUDENT.value,
        is_active=True,
        must_change_password=False,
    )
    db_session.add(student2)
    db_session.commit()
    db_session.refresh(student2)
    return student2


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    token, _, _ = create_access_token(admin_user.id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_headers(student_user: User) -> dict[str, str]:
    token, _, _ = create_access_token(student_user.id, student_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def student_2_headers(student_user_2: User) -> dict[str, str]:
    token, _, _ = create_access_token(student_user_2.id, student_user_2.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_category(db_session: Session) -> Category:
    cat = Category(name="Bilgisayar Bilimi", description="Yazılım ve sistem kitapları", is_active=True)
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture
def sample_book(db_session: Session, sample_category: Category) -> Book:
    book = Book(
        isbn="9780132350884",
        title="Temiz Kod",
        author="Robert C. Martin",
        publisher="Prentice Hall",
        publication_year=2008,
        category_id=sample_category.id,
        shelf_location="A-101",
        total_copies=3,
        available_copies=3,
        is_active=True,
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book
