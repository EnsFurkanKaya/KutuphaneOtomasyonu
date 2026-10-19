"""Kullanıcı veri erişimi."""
from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import Role
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)

    def get_for_update(self, user_id: int) -> User | None:
        """Satırı kilitler; aynı öğrencinin eşzamanlı ödünç isteklerini sıraya sokar."""
        return self.session.execute(
            select(User).where(User.id == user_id).with_for_update().execution_options(populate_existing=True)
        ).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        return self.session.execute(select(User).where(User.email == email.lower())).scalar_one_or_none()

    def get_by_student_number(self, student_number: str) -> User | None:
        return self.session.execute(
            select(User).where(User.student_number == student_number)
        ).scalar_one_or_none()

    def add(self, user: User) -> User:
        self.session.add(user)
        return user

    def list(
        self,
        *,
        q: str | None,
        role: Role | None,
        is_active: bool | None,
        offset: int,
        limit: int,
    ) -> tuple[list[User], int]:
        stmt = select(User)
        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(
                or_(User.full_name.ilike(pattern), User.email.ilike(pattern), User.student_number.ilike(pattern))
            )
        if role is not None:
            stmt = stmt.where(User.role == role.value)
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
        total = self.session.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        items = self.session.execute(stmt.order_by(User.full_name, User.id).offset(offset).limit(limit)).scalars().all()
        return list(items), total

    def count_active_students(self) -> int:
        return self.session.execute(
            select(func.count(User.id)).where(User.role == Role.STUDENT.value, User.is_active.is_(True))
        ).scalar_one()
