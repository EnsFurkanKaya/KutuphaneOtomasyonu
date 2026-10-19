"""Raporlama iş akışları. Raporlar yalnızca okuma yapar; kayıt geçmişini değiştirmez (Kural 17)."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.config import get_settings
from app.domain.errors import BusinessRuleError
from app.repositories.book_repository import BookRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.user_repository import UserRepository
from app.schemas.report import ActivityItem, DashboardStats, OverdueItem, OverdueReport

RECENT_ACTIVITY_LIMIT = 10


class ReportService:
    def __init__(self, session: Session):
        self.session = session
        self.loans = LoanRepository(session)
        self.books = BookRepository(session)
        self.users = UserRepository(session)
        self.categories = CategoryRepository(session)
        self.tz = ZoneInfo(get_settings().app_timezone)

    def _start_of_day(self, d: date) -> datetime:
        return datetime.combine(d, time.min, tzinfo=self.tz)

    def overdue_report(
        self,
        *,
        start_date: date | None,
        end_date: date | None,
        user_id: int | None,
        book_id: int | None,
        student: str | None,
        book: str | None,
        page: int,
        page_size: int,
    ) -> OverdueReport:
        """Tarih aralığı, son iade tarihine (due_at) göre ve kütüphanenin saat diliminde uygulanır."""
        if start_date and end_date and start_date > end_date:
            raise BusinessRuleError("Başlangıç tarihi bitiş tarihinden sonra olamaz.", "GECERSIZ_TARIH_ARALIGI")
        now = utcnow()
        due_from = self._start_of_day(start_date) if start_date else None
        due_to = self._start_of_day(end_date + timedelta(days=1)) if end_date else None
        loans, total = self.loans.overdue(
            now=now,
            due_from=due_from,
            due_to=due_to,
            user_id=user_id,
            book_id=book_id,
            student=student,
            book=book,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        items = [
            OverdueItem(
                loan_id=loan.id,
                user_id=loan.user.id,
                student_number=loan.user.student_number,
                full_name=loan.user.full_name,
                email=loan.user.email,
                book_id=loan.book.id,
                book_title=loan.book.title,
                isbn=loan.book.isbn,
                borrowed_at=loan.borrowed_at,
                due_at=loan.due_at,
                overdue_days=loan.overdue_days(now),
            )
            for loan in loans
        ]
        pages = (total + page_size - 1) // page_size if total else 0
        return OverdueReport(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            generated_at=now,
            start_date=start_date,
            end_date=end_date,
        )

    def dashboard(self) -> DashboardStats:
        now = utcnow()
        titles, total_copies, available = self.books.stats()
        activity: list[ActivityItem] = []
        for loan in self.loans.recent_borrows(RECENT_ACTIVITY_LIMIT):
            activity.append(
                ActivityItem(
                    loan_id=loan.id,
                    type="BORROW",
                    occurred_at=loan.borrowed_at,
                    student_number=loan.user.student_number,
                    full_name=loan.user.full_name,
                    book_title=loan.book.title,
                )
            )
        for loan in self.loans.recent_returns(RECENT_ACTIVITY_LIMIT):
            assert loan.returned_at is not None
            activity.append(
                ActivityItem(
                    loan_id=loan.id,
                    type="RETURN",
                    occurred_at=loan.returned_at,
                    student_number=loan.user.student_number,
                    full_name=loan.user.full_name,
                    book_title=loan.book.title,
                )
            )
        activity.sort(key=lambda a: a.occurred_at, reverse=True)
        return DashboardStats(
            active_book_titles=titles,
            total_copies=total_copies,
            available_copies=available,
            active_loans=self.loans.count_active(),
            overdue_loans=self.loans.count_overdue(now),
            active_students=self.users.count_active_students(),
            total_categories=self.categories.count_active(),
            recent_activity=activity[:RECENT_ACTIVITY_LIMIT],
            generated_at=now,
        )
