"""Kitap veri erişimi."""
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.book import Book
from app.models.category import Category
from app.models.loan import Loan

SORT_COLUMNS = {
    "title": Book.title,
    "author": Book.author,
    "publication_year": Book.publication_year,
    "created_at": Book.created_at,
    "available_copies": Book.available_copies,
}


class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, book_id: int) -> Book | None:
        return self.session.execute(
            select(Book).options(selectinload(Book.category)).where(Book.id == book_id)
        ).scalar_one_or_none()

    def get_for_update(self, book_id: int) -> Book | None:
        """SELECT ... FOR UPDATE: aynı kitabın stoğu üzerinde eşzamanlı değişiklikleri sıraya sokar."""
        return self.session.execute(
            select(Book).where(Book.id == book_id).with_for_update().execution_options(populate_existing=True)
        ).scalar_one_or_none()

    def get_by_isbn(self, isbn: str) -> Book | None:
        return self.session.execute(select(Book).where(Book.isbn == isbn)).scalar_one_or_none()

    def search(
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
        offset: int,
        limit: int,
    ) -> tuple[list[Book], int]:
        stmt = select(Book).outerjoin(Category, Book.category_id == Category.id)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    Book.title.ilike(pattern),
                    Book.author.ilike(pattern),
                    Book.isbn.ilike(f"%{q.replace('-', '').replace(' ', '')}%"),
                    Category.name.ilike(pattern),
                )
            )
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))
        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))
        if isbn:
            stmt = stmt.where(Book.isbn.ilike(f"%{isbn.replace('-', '').replace(' ', '')}%"))
        if category_id is not None:
            stmt = stmt.where(Book.category_id == category_id)
        if available_only:
            stmt = stmt.where(Book.available_copies > 0)
        if not include_inactive:
            stmt = stmt.where(Book.is_active.is_(True))

        total = self.session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        column = SORT_COLUMNS.get(sort, Book.title)
        ordering = column.desc().nulls_last() if order == "desc" else column.asc().nulls_last()
        items = (
            self.session.execute(
                stmt.options(selectinload(Book.category)).order_by(ordering, Book.id).offset(offset).limit(limit)
            )
            .scalars()
            .all()
        )
        return list(items), total

    def has_any_loans(self, book_id: int) -> bool:
        return self.session.execute(select(Loan.id).where(Loan.book_id == book_id).limit(1)).first() is not None

    def add(self, book: Book) -> Book:
        self.session.add(book)
        return book

    def delete(self, book: Book) -> None:
        self.session.delete(book)

    def stats(self) -> tuple[int, int, int]:
        """(aktif başlık sayısı, toplam kopya, uygun kopya) — yalnızca aktif kitaplar."""
        row = self.session.execute(
            select(
                func.count(Book.id),
                func.coalesce(func.sum(Book.total_copies), 0),
                func.coalesce(func.sum(Book.available_copies), 0),
            ).where(Book.is_active.is_(True))
        ).one()
        return int(row[0]), int(row[1]), int(row[2])
