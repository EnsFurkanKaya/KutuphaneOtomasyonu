"""Kullanıcı (öğrenci / yönetici) varlığı."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, UniqueConstraint, false, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.domain import rules
from app.domain.enums import Role
from app.domain.errors import PermissionDeniedError

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.loan import Loan


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("student_number", name="uq_users_student_number"),
        CheckConstraint("role IN ('STUDENT', 'ADMIN')", name="role_valid"),
        CheckConstraint("role = 'ADMIN' OR student_number IS NOT NULL", name="student_has_number"),
        CheckConstraint("failed_login_attempts >= 0", name="failed_logins_non_negative"),
    )
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=Role.STUDENT.value, server_default=Role.STUDENT.value)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=true())
    must_change_password: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    loans: Mapped[list[Loan]] = relationship(back_populates="user")

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN.value

    def borrow_book(
        self,
        book: Book,
        *,
        now: datetime,
        loan_period_days: int,
        active_loan_count: int,
        max_active_loans: int,
        already_has_active_loan_for_book: bool,
    ) -> Loan:
        """UML: borrowBook(). İş kurallarını doğrular ve yeni bir ödünç kaydı üretir."""
        from app.models.loan import Loan

        rules.ensure_can_borrow(
            role=self.role,
            user_is_active=self.is_active,
            active_loan_count=active_loan_count,
            max_active_loans=max_active_loans,
            book_is_active=book.is_active,
            available_copies=book.available_copies,
            already_has_active_loan_for_book=already_has_active_loan_for_book,
        )
        return Loan.borrow(self, book, borrowed_at=now, loan_period_days=loan_period_days)

    def return_book(self, loan: Loan, *, now: datetime) -> None:
        """UML: returnBook(). Öğrenci yalnızca kendi kaydını, yönetici her kaydı iade edebilir."""
        if not self.is_admin and loan.user_id != self.id:
            raise PermissionDeniedError("Bu ödünç kaydı size ait değil.", "KAYIT_SIZE_AIT_DEGIL")
        loan.return_book(now)
