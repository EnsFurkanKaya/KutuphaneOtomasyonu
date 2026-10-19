"""Kitap kataloğu ve stok yönetimi iş akışları."""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import transaction
from app.domain.enums import DeleteAction
from app.domain.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.book import Book
from app.models.category import Category
from app.repositories.book_repository import BookRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.loan_repository import LoanRepository
from app.schemas.book import BookCreate, BookOut, BookUpdate, DeleteResult
from app.schemas.common import make_page

DUPLICATE_ISBN = "Bu ISBN ile kayıtlı bir kitap zaten var."
OPTIONAL_TEXT_FIELDS = ("description", "publisher", "shelf_location")


class BookService:
    def __init__(self, session: Session):
        self.session = session
        self.books = BookRepository(session)
        self.categories = CategoryRepository(session)
        self.loans = LoanRepository(session)

    def _active_category(self, category_id: int) -> Category:
        category = self.categories.get(category_id)
        if category is None:
            raise NotFoundError("Seçilen kategori bulunamadı.", "KATEGORI_BULUNAMADI")
        if not category.is_active:
            raise BusinessRuleError("Pasif bir kategoriye kitap atanamaz.", "KATEGORI_PASIF")
        return category

    def search_books(
        self,
        *,
        q: str | None,
        title: str | None,
        author: str | None,
        isbn: str | None,
        category_id: int | None,
        available_only: bool,
        include_inactive: bool,
        sort: str,
        order: str,
        page: int,
        page_size: int,
    ) -> dict:
        """UML: User.searchBooks(). İsim, yazar, ISBN ve kategoriye göre arama + filtre + sıralama + sayfalama."""
        items, total = self.books.search(
            q=q,
            title=title,
            author=author,
            isbn=isbn,
            category_id=category_id,
            available_only=available_only,
            include_inactive=include_inactive,
            sort=sort,
            order=order,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        return make_page([BookOut.model_validate(b) for b in items], total, page, page_size)

    def get_book(self, book_id: int, *, include_inactive: bool) -> Book:
        book = self.books.get(book_id)
        if book is None or (not book.is_active and not include_inactive):
            raise NotFoundError("Kitap bulunamadı.")
        return book

    def create(self, data: BookCreate) -> Book:
        if self.books.get_by_isbn(data.isbn):
            raise ConflictError(DUPLICATE_ISBN, "ISBN_KULLANIMDA")
        book = Book(
            isbn=data.isbn,
            title=data.title,
            author=data.author,
            description=data.description or None,
            publisher=data.publisher or None,
            publication_year=data.publication_year,
            shelf_location=data.shelf_location or None,
            total_copies=data.total_copies,
            available_copies=data.total_copies,
            is_active=True,
        )
        if data.category_id is not None:
            self._active_category(data.category_id).add_book(book)
        try:
            with transaction(self.session):
                self.books.add(book)
                self.session.flush()
        except IntegrityError as exc:
            raise ConflictError(DUPLICATE_ISBN, "ISBN_KULLANIMDA") from exc
        return self.get_book(book.id, include_inactive=True)

    def update(self, book_id: int, data: BookUpdate) -> Book:
        changes = data.model_dump(exclude_unset=True)
        try:
            with transaction(self.session):
                book = self.books.get_for_update(book_id)
                if book is None:
                    raise NotFoundError("Kitap bulunamadı.")
                if "isbn" in changes and changes["isbn"] != book.isbn:
                    existing = self.books.get_by_isbn(changes["isbn"])
                    if existing and existing.id != book.id:
                        raise ConflictError(DUPLICATE_ISBN, "ISBN_KULLANIMDA")
                if "category_id" in changes:
                    new_category_id = changes.pop("category_id")
                    current = book.category
                    if new_category_id is None:
                        if current is not None:
                            current.remove_book(book)
                    elif current is None or current.id != new_category_id:
                        target = self._active_category(new_category_id)
                        if current is not None:
                            current.remove_book(book)
                        target.add_book(book)
                for field in OPTIONAL_TEXT_FIELDS:
                    if field in changes and changes[field] == "":
                        changes[field] = None
                book.update_details(**changes)
        except IntegrityError as exc:
            raise ConflictError(DUPLICATE_ISBN, "ISBN_KULLANIMDA") from exc
        return self.get_book(book_id, include_inactive=True)

    def update_stock(self, book_id: int, total_copies: int) -> Book:
        """Stok güncellemesi kitap satırı kilitlenerek tek transaction içinde yapılır."""
        with transaction(self.session):
            book = self.books.get_for_update(book_id)
            if book is None:
                raise NotFoundError("Kitap bulunamadı.")
            active_loans = self.loans.count_active_for_book(book.id)
            book.update_stock(total_copies, active_loans)
        return self.get_book(book_id, include_inactive=True)

    def delete(self, book_id: int) -> DeleteResult:
        """Kural 12: Ödünç geçmişi olan kitap fiziksel olarak silinmez, pasifleştirilir."""
        with transaction(self.session):
            book = self.books.get_for_update(book_id)
            if book is None:
                raise NotFoundError("Kitap bulunamadı.")
            if self.books.has_any_loans(book.id):
                book.is_active = False
                result = DeleteResult(
                    id=book_id,
                    action=DeleteAction.DEACTIVATED,
                    message="Kitabın ödünç geçmişi olduğu için fiziksel olarak silinmedi; pasifleştirildi.",
                )
            else:
                self.books.delete(book)
                result = DeleteResult(id=book_id, action=DeleteAction.DELETED, message="Kitap kalıcı olarak silindi.")
        return result
