"""Ödünç alma ve iade endpoint'leri."""
from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, CurrentUser, DbSession, StudentUser
from app.api.routers.docs import error_responses
from app.core.clock import utcnow
from app.schemas.common import Page
from app.schemas.loan import LoanCreate, LoanOut, LoanStatusFilter
from app.services.loan_service import LoanService, loan_to_out

router = APIRouter(prefix="/loans", tags=["Ödünç ve İade"])


@router.post(
    "",
    response_model=LoanOut,
    status_code=status.HTTP_201_CREATED,
    summary="Kitap ödünç alır (öğrenci)",
    responses=error_responses(400, 401, 403, 404, 409, 422),
)
def borrow_book(data: LoanCreate, user: StudentUser, db: DbSession) -> LoanOut:
    loan = LoanService(db).borrow(user.id, data.book_id)
    return loan_to_out(loan, utcnow())


@router.get(
    "",
    response_model=Page[LoanOut],
    summary="Tüm ödünç işlemlerini listeler (yönetici)",
    responses=error_responses(401, 403, 422),
)
def list_loans(
    _: AdminUser,
    db: DbSession,
    status: LoanStatusFilter = "all",
    user_id: int | None = Query(None, gt=0),
    book_id: int | None = Query(None, gt=0),
    q: str | None = Query(None, max_length=100, description="Öğrenci adı/numarası, kitap adı veya ISBN"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    return LoanService(db).list_loans(
        status=status, user_id=user_id, book_id=book_id, q=q, page=page, page_size=page_size
    )


@router.get(
    "/my",
    response_model=Page[LoanOut],
    summary="Kendi ödünç kayıtlarım",
    responses=error_responses(401, 422),
)
def my_loans(
    user: CurrentUser,
    db: DbSession,
    status: LoanStatusFilter = "all",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    return LoanService(db).list_loans(
        status=status, user_id=user.id, book_id=None, q=None, page=page, page_size=page_size
    )


@router.get(
    "/{loan_id}",
    response_model=LoanOut,
    summary="Ödünç kaydı ayrıntısı (sahibi veya yönetici)",
    responses=error_responses(401, 403, 404),
)
def get_loan(loan_id: int, user: CurrentUser, db: DbSession) -> LoanOut:
    return loan_to_out(LoanService(db).get_loan(loan_id, user), utcnow())


@router.post(
    "/{loan_id}/return",
    response_model=LoanOut,
    summary="Kitabı iade eder (sahibi veya yönetici)",
    responses=error_responses(400, 401, 403, 404, 409),
)
def return_book(loan_id: int, user: CurrentUser, db: DbSession) -> LoanOut:
    return loan_to_out(LoanService(db).return_loan(loan_id, user), utcnow())
