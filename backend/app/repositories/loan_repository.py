"""Ödünç kaydı veri erişimi."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User


def _apply_status(stmt: Select, status: str, now: datetime) -> Select:
    if status == "active":
        return stmt.where(Loan.returned_at.is_(None))
    if status == "overdue":
        return stmt.where(Loan.returned_at.is_(None), Loan.due_at < now)
    if status == "returned":
        return stmt.where(Loan.returned_at.is_not(None))
    return stmt


class LoanRepository:
    def __init__(self, session: Session):
        self.session = session

    def _with_relations(self) -> Select:
        return select(Loan).options(joinedload(Loan.user), joinedload(Loan.book))

    def get(self, loan_id: int) -> Loan | None:
        return self.session.execute(self._with_relations().where(Loan.id == loan_id)).scalar_one_or_none()

    def get_for_update(self, loan_id: int) -> Loan | None:
        """Ödünç satırını kilitler; aynı kaydın eşzamanlı iki kez iade edilmesini engeller."""
        return self.session.execute(
            select(Loan).where(Loan.id == loan_id).with_for_update().execution_options(populate_existing=True)
        ).scalar_one_or_none()

    def add(self, loan: Loan) -> Loan:
        self.session.add(loan)
        return loan

    def count_active_for_user(self, user_id: int) -> int:
        return self.session.execute(
            select(func.count(Loan.id)).where(Loan.user_id == user_id, Loan.returned_at.is_(None))
        ).scalar_one()

    def count_active_for_book(self, book_id: int) -> int:
        return self.session.execute(
            select(func.count(Loan.id)).where(Loan.book_id == book_id, Loan.returned_at.is_(None))
        ).scalar_one()

    def has_active_loan(self, user_id: int, book_id: int) -> bool:
        return (
            self.session.execute(
                select(Loan.id).where(
                    Loan.user_id == user_id, Loan.book_id == book_id, Loan.returned_at.is_(None)
                )
            ).first()
            is not None
        )

    def list(
        self,
        *,
        now: datetime,
        status: str,
        user_id: int | None,
        book_id: int | None,
        q: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Loan], int]:
        stmt = select(Loan).join(User, Loan.user_id == User.id).join(Book, Loan.book_id == Book.id)
        stmt = _apply_status(stmt, status, now)
        if user_id is not None:
            stmt = stmt.where(Loan.user_id == user_id)
        if book_id is not None:
            stmt = stmt.where(Loan.book_id == book_id)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(
                    User.full_name.ilike(pattern),
                    User.student_number.ilike(pattern),
                    Book.title.ilike(pattern),
                    Book.isbn.ilike(pattern),
                )
            )
        total = self.session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        items = (
            self.session.execute(
                stmt.options(joinedload(Loan.user), joinedload(Loan.book))
                .order_by(Loan.borrowed_at.desc(), Loan.id.desc())
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(items), total

    def overdue(
        self,
        *,
        now: datetime,
        due_from: datetime | None,
        due_to: datetime | None,
        user_id: int | None,
        book_id: int | None,
        student: str | None,
        book: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Loan], int]:
        """Kural 9-11: iade edilmemiş ve son iade tarihi geçmiş kayıtlar."""
        stmt = (
            select(Loan)
            .join(User, Loan.user_id == User.id)
            .join(Book, Loan.book_id == Book.id)
            .where(Loan.returned_at.is_(None), Loan.due_at < now)
        )
        if due_from is not None:
            stmt = stmt.where(Loan.due_at >= due_from)
        if due_to is not None:
            stmt = stmt.where(Loan.due_at < due_to)
        if user_id is not None:
            stmt = stmt.where(Loan.user_id == user_id)
        if book_id is not None:
            stmt = stmt.where(Loan.book_id == book_id)
        if student:
            pattern = f"%{student}%"
            stmt = stmt.where(or_(User.full_name.ilike(pattern), User.student_number.ilike(pattern)))
        if book:
            pattern = f"%{book}%"
            stmt = stmt.where(or_(Book.title.ilike(pattern), Book.isbn.ilike(pattern)))
        total = self.session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        items = (
            self.session.execute(
                stmt.options(joinedload(Loan.user), joinedload(Loan.book))
                .order_by(Loan.due_at.asc(), Loan.id.asc())
                .offset(offset)
                .limit(limit)
            )
            .scalars()
            .all()
        )
        return list(items), total

    def count_active(self) -> int:
        return self.session.execute(select(func.count(Loan.id)).where(Loan.returned_at.is_(None))).scalar_one()

    def count_overdue(self, now: datetime) -> int:
        return self.session.execute(
            select(func.count(Loan.id)).where(and_(Loan.returned_at.is_(None), Loan.due_at < now))
        ).scalar_one()

    def recent_borrows(self, limit: int) -> list[Loan]:
        return list(
            self.session.execute(self._with_relations().order_by(Loan.borrowed_at.desc()).limit(limit))
            .scalars()
            .all()
        )

    def recent_returns(self, limit: int) -> list[Loan]:
        return list(
            self.session.execute(
                self._with_relations()
                .where(Loan.returned_at.is_not(None))
                .order_by(Loan.returned_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
