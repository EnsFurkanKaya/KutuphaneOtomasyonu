"""Kategori varlığı."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String, Text, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain.errors import BusinessRuleError

if TYPE_CHECKING:
    from app.models.book import Book


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (CheckConstraint("length(trim(name)) >= 2", name="name_min_length"),)
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    books: Mapped[list[Book]] = relationship(back_populates="category")

    def add_book(self, book: Book) -> None:
        """UML: addBook(). Kitabı bu kategoriye atar."""
        if not self.is_active:
            raise BusinessRuleError("Pasif bir kategoriye kitap atanamaz.", "KATEGORI_PASIF")
        book.category = self

    def remove_book(self, book: Book) -> None:
        """UML: removeBook(). Kitabın bu kategoriyle ilişkisini kaldırır."""
        if book.category_id != self.id and book.category is not self:
            raise BusinessRuleError("Kitap bu kategoriye ait değil.", "KITAP_KATEGORIDE_DEGIL")
        book.category = None


# Kategori adı büyük/küçük harf duyarsız benzersizdir ("Bilgisayar" == "bilgisayar").
Index("uq_categories_name_lower", func.lower(Category.name), unique=True)
