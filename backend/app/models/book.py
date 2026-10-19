"""Kitap varlığı ve stok kuralları."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain import rules
from app.domain.errors import BusinessRuleError, ConflictError

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.loan import Loan


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_books_isbn"),
        CheckConstraint("total_copies >= 0", name="total_copies_non_negative"),
        CheckConstraint("available_copies >= 0", name="available_copies_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="available_not_exceed_total"),
        CheckConstraint(
            "publication_year IS NULL OR publication_year BETWEEN 1450 AND 2100", name="publication_year_range"
        ),
        Index("ix_books_title", "title"),
        Index("ix_books_author", "author"),
        Index("ix_books_category_id", "category_id"),
        Index("ix_books_is_active", "is_active"),
    )
    __mapper_args__ = {"eager_defaults": True}

    # update_details() ile değiştirilebilecek alanlar (stok alanları hariç)
    DETAIL_FIELDS = frozenset(
        {"isbn", "title", "author", "description", "publisher", "publication_year", "shelf_location", "is_active"}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(160), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT", name="fk_books_category_id_categories"), nullable=True
    )
    shelf_location: Mapped[str | None] = mapped_column(String(40), nullable=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    available_copies: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    category: Mapped[Category | None] = relationship(back_populates="books")
    loans: Mapped[list[Loan]] = relationship(back_populates="book")

    def is_available(self) -> bool:
        """UML: isAvailable(). Kitap aktif ve en az bir uygun kopyası varsa True."""
        return self.is_active and self.available_copies > 0

    def update_stock(self, new_total: int, active_loan_count: int) -> None:
        """UML: updateStock(). Toplam kopyayı değiştirir, mevcut kopyayı tutarlı hesaplar."""
        self.available_copies = rules.calculate_available_after_stock_change(new_total, active_loan_count)
        self.total_copies = new_total

    def update_details(self, **changes: Any) -> None:
        """UML: updateDetails(). Stok dışındaki kitap bilgilerini günceller."""
        for field, value in changes.items():
            if field not in self.DETAIL_FIELDS:
                raise BusinessRuleError(f"'{field}' alanı bu işlemle güncellenemez.", "GECERSIZ_ALAN")
            setattr(self, field, value)

    def _decrease_available(self) -> None:
        """Ödünç verildiğinde mevcut stok bir azalır (Kural 6). Stok asla negatif olmaz (Kural 4)."""
        if not self.is_active:
            raise BusinessRuleError("Bu kitap pasif durumda olduğu için ödünç verilemez.", "KITAP_PASIF")
        if self.available_copies <= 0:
            raise BusinessRuleError("Bu kitabın şu anda ödünç verilebilecek kopyası yok.", "STOK_YOK")
        self.available_copies -= 1

    def _increase_available(self) -> None:
        """İade edildiğinde mevcut stok bir artar (Kural 7)."""
        if self.available_copies >= self.total_copies:
            raise ConflictError("Stok tutarsızlığı: mevcut kopya toplam kopyayı aşamaz.", "STOK_TUTARSIZ")
        self.available_copies += 1
