"""Kullanıcı (profil) ve yönetici kullanıcı yönetimi endpoint'leri."""
from fastapi import APIRouter, Query

from app.api.deps import AdminUser, AuthenticatedUser, CurrentUser, DbSession
from app.api.routers.docs import error_responses
from app.domain.enums import Role
from app.schemas.common import MessageResponse, Page
from app.schemas.loan import LoanOut, LoanStatusFilter
from app.schemas.user import AdminUserUpdate, ChangePasswordRequest, UpdateMeRequest, UserOut
from app.services.loan_service import LoanService
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Kullanıcılar"])


@router.get("/me", response_model=UserOut, summary="Profil bilgilerim", responses=error_responses(401))
def get_me(user: AuthenticatedUser) -> UserOut:
    return UserOut.model_validate(user)


@router.patch(
    "/me",
    response_model=UserOut,
    summary="Profilimi günceller (yalnızca ad soyad)",
    responses=error_responses(401, 403, 422),
)
def update_me(data: UpdateMeRequest, user: CurrentUser, db: DbSession) -> UserOut:
    return UserOut.model_validate(UserService(db).update_me(user, data))


@router.patch(
    "/me/password",
    response_model=MessageResponse,
    summary="Parolamı değiştirir",
    responses=error_responses(400, 401, 422),
)
def change_password(data: ChangePasswordRequest, user: AuthenticatedUser, db: DbSession) -> MessageResponse:
    UserService(db).change_password(user, data)
    return MessageResponse(message="Parolanız başarıyla değiştirildi.")


@router.get(
    "/me/loans",
    response_model=Page[LoanOut],
    summary="Kendi ödünç kayıtlarım (aktif, gecikmiş, iade edilmiş)",
    responses=error_responses(401, 403, 422),
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


# ----- Yalnızca yönetici -----


@router.get(
    "",
    response_model=Page[UserOut],
    summary="Kullanıcıları listeler (yönetici)",
    responses=error_responses(401, 403, 422),
)
def list_users(
    _: AdminUser,
    db: DbSession,
    q: str | None = Query(None, max_length=100, description="Ad, e-posta veya öğrenci numarası"),
    role: Role | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> dict:
    return UserService(db).list_users(q=q, role=role, is_active=is_active, page=page, page_size=page_size)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Kullanıcı ayrıntısı (yönetici)",
    responses=error_responses(401, 403, 404),
)
def get_user(user_id: int, _: AdminUser, db: DbSession) -> UserOut:
    return UserOut.model_validate(UserService(db).get_user(user_id))


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Kullanıcıyı aktif/pasif yapar veya adını günceller (yönetici)",
    responses=error_responses(400, 401, 403, 404, 422),
)
def update_user(user_id: int, data: AdminUserUpdate, admin: AdminUser, db: DbSession) -> UserOut:
    return UserOut.model_validate(UserService(db).admin_update(admin, user_id, data))
