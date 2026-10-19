"""Ödünç alma ve iade iş akışları.

Her iki işlem de tek bir veritabanı transaction'ı içinde, ilgili satırlar
SELECT ... FOR UPDATE ile kilitlenerek yürütülür. Böylece:
  * aynı son kopya iki öğrenciye verilemez,
  * aynı öğrenci eşzamanlı isteklerle limiti aşamaz,
  * aynı ödünç kaydı iki kez iade edilip stok iki kez artırılamaz.
"""
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.config import get_settings
from app.db.session import transaction
from app.domain.errors import ConflictError, NotFoundError, PermissionDeniedError
from app.models.loan import Loan
from app.models.user import User
from app.repositories.book_repository import BookRepository
from app.repositories.loan_repository import LoanRepository
from app.repositories.user_repository import UserRepository
from app.schemas.book import BookSummary
from app.schemas.common import make_page
from app.schemas.loan import LoanOut
from app.schemas.user import UserSummary


def loan_to_out(loan: Loan, now: datetime) -> LoanOut:
    return LoanOut(
        id=loan.id,
        user=UserSummary.model_validate(loan.user),
        book=BookSummary.model_validate(loan.book),
        borrowed_at=loan.borrowed_at,
        due_at=loan.due_at,
        returned_at=loan.returned_at,
        status=loan.status(now),
        is_overdue=loan.is_overdue(now),
        overdue_days=loan.overdue_days(now),
        late_return_days=loan.late_return_days(),
    )


class LoanService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.books = BookRepository(session)
        self.loans = LoanRepository(session)
        self.settings = get_settings()

    def borrow(self, user_id: int, book_id: int) -> Loan:
        try:
            with transaction(self.session):
                # 1-2. Kullanıcıyı kilitle (aynı öğrencinin paralel istekleri sıraya girer)
                user = self.users.get_for_update(user_id)
                if user is None:
                    raise NotFoundError("Kullanıcı bulunamadı.")
                # 4-5. Kitabı kilitle; stok başka bir transaction tarafından değiştirilemez
                book = self.books.get_for_update(book_id)
                if book is None:
                    raise NotFoundError("Kitap bulunamadı.")
                # 3. Mevcut aktif ödünç sayısı ve aynı kitap kontrolü
                active_count = self.loans.count_active_for_user(user.id)
                already = self.loans.has_active_loan(user.id, book.id)
                # 6-7. İş kuralları doğrulanır, kayıt oluşturulur, stok azaltılır
                loan = user.borrow_book(
                    book,
                    now=utcnow(),
                    loan_period_days=self.settings.loan_period_days,
                    active_loan_count=active_count,
                    max_active_loans=self.settings.max_active_loans,
                    already_has_active_loan_for_book=already,
                )
                self.loans.add(loan)
                self.session.flush()
            # 8. Başarılıysa commit edildi; hata olursa transaction() rollback yaptı
        except IntegrityError as exc:
            raise ConflictError("Bu kitap için zaten aktif bir ödünç kaydınız var.", "AYNI_KITAP_ZATEN_ODUNCTE") from exc
        return loan

    def return_loan(self, loan_id: int, actor: User) -> Loan:
        with transaction(self.session):
            loan = self.loans.get_for_update(loan_id)
            if loan is None:
                raise NotFoundError("Ödünç kaydı bulunamadı.")
            if not actor.is_admin and loan.user_id != actor.id:
                raise PermissionDeniedError("Bu ödünç kaydı size ait değil.", "KAYIT_SIZE_AIT_DEGIL")
            self.books.get_for_update(loan.book_id)  # stok satırını kilitle
            actor.return_book(loan, now=utcnow())
        result = self.loans.get(loan_id)
        assert result is not None
        return result

    def get_loan(self, loan_id: int, actor: User) -> Loan:
        loan = self.loans.get(loan_id)
        if loan is None:
            raise NotFoundError("Ödünç kaydı bulunamadı.")
        if not actor.is_admin and loan.user_id != actor.id:
            raise PermissionDeniedError("Başka bir öğrencinin ödünç kaydını görüntüleyemezsiniz.", "KAYIT_SIZE_AIT_DEGIL")
        return loan

    def list_loans(
        self,
        *,
        status: str,
        user_id: int | None,
        book_id: int | None,
        q: str | None,
        page: int,
        page_size: int,
    ) -> dict:
        now = utcnow()
        items, total = self.loans.list(
            now=now,
            status=status,
            user_id=user_id,
            book_id=book_id,
            q=q,
            offset=(page - 1) * page_size,
            limit=page_size,
        )
        return make_page([loan_to_out(loan, now) for loan in items], total, page, page_size)
