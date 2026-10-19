"""Ödünç kaydı varlığı."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain import rules
from app.domain.enums import LoanStatus
from app.domain.errors import BusinessRuleError, ConflictError

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class Loan(Base):
    __tablename__ = "loans"
    __table_args__ = (
        CheckConstraint("due_at > borrowed_at", name="due_after_borrow"),
        CheckConstraint("returned_at IS NULL OR returned_at >= borrowed_at", name="return_after_borrow"),
        Index("ix_loans_user_id", "user_id"),
        Index("ix_loans_book_id", "book_id"),
        Index("ix_loans_borrowed_at", "borrowed_at"),
        # Kural 5: Aynı öğrenci aynı kitap için yalnızca bir aktif ödünç kaydına sahip olabilir.
        Index(
            "uq_loans_active_user_book",
            "user_id",
            "book_id",
            unique=True,
            postgresql_where=text("returned_at IS NULL"),
            sqlite_where=text("returned_at IS NULL"),
        ),
        # Gecikme raporu sorgularını hızlandırır.
        Index("ix_loans_active_due_at", "due_at", postgresql_where=text("returned_at IS NULL")),
    )
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT", name="fk_loans_user_id_users"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="RESTRICT", name="fk_loans_book_id_books"), nullable=False
    )
    borrowed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship(back_populates="loans")
    book: Mapped[Book] = relationship(back_populates="loans")

    @classmethod
    def borrow(cls, user: User, book: Book, *, borrowed_at: datetime, loan_period_days: int) -> Loan:
        """UML: borrow(). Stoku bir azaltır ve son iade tarihi hesaplanmış yeni kayıt döndürür."""
        book._decrease_available()
        return cls(
            user=user,
            book=book,
            borrowed_at=borrowed_at,
            due_at=rules.calculate_due_date(borrowed_at, loan_period_days),
        )

    def return_book(self, now: datetime) -> None:
        """UML: returnBook(). Aynı kayıt yalnızca bir kez iade edilebilir (Kural 8)."""
        if self.returned_at is not None:
            raise ConflictError("Bu ödünç kaydı zaten iade edilmiş.", "ZATEN_IADE_EDILDI")
        if rules._normalize_dt(now) < rules._normalize_dt(self.borrowed_at):
            raise BusinessRuleError("İade tarihi ödünç tarihinden önce olamaz.", "GECERSIZ_IADE_TARIHI")
        self.returned_at = now
        self.book._increase_available()

    @property
    def is_active(self) -> bool:
        return self.returned_at is None

    def is_overdue(self, now: datetime) -> bool:
        """UML: isOverdue()."""
        return rules.is_overdue(self.due_at, self.returned_at, now)

    def overdue_days(self, now: datetime) -> int:
        return rules.overdue_days(self.due_at, self.returned_at, now)

    def late_return_days(self) -> int:
        return rules.late_return_days(self.due_at, self.returned_at)

    def status(self, now: datetime) -> LoanStatus:
        return rules.loan_status(self.due_at, self.returned_at, now)
