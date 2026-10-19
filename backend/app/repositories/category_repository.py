"""Kategori veri erişimi."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.category import Category


class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_name(self, name: str) -> Category | None:
        """Büyük/küçük harf duyarsız arama."""
        return self.session.execute(
            select(Category).where(func.lower(Category.name) == name.strip().lower())
        ).scalar_one_or_none()

    def list_with_counts(self, *, include_inactive: bool) -> list[tuple[Category, int]]:
        book_count = (
            select(func.count(Book.id)).where(Book.category_id == Category.id).correlate(Category).scalar_subquery()
        )
        stmt = select(Category, book_count.label("book_count")).order_by(Category.name)
        if not include_inactive:
            stmt = stmt.where(Category.is_active.is_(True))
        return [(row[0], row[1]) for row in self.session.execute(stmt).all()]

    def count_books(self, category_id: int) -> int:
        return self.session.execute(
            select(func.count(Book.id)).where(Book.category_id == category_id)
        ).scalar_one()

    def count_active(self) -> int:
        return self.session.execute(
            select(func.count(Category.id)).where(Category.is_active.is_(True))
        ).scalar_one()

    def add(self, category: Category) -> Category:
        self.session.add(category)
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
