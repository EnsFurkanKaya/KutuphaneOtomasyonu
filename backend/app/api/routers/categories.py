"""Kategori endpoint'leri."""
from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.api.routers.docs import error_responses
from app.schemas.book import DeleteResult
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Kategoriler"])


@router.get("", response_model=list[CategoryOut], summary="Kategorileri listeler", responses=error_responses(401))
def list_categories(
    user: CurrentUser,
    db: DbSession,
    include_inactive: bool = Query(False, description="Pasif kategorileri de getir (yalnızca yönetici)"),
) -> list[CategoryOut]:
    return CategoryService(db).list_categories(include_inactive=include_inactive and user.is_admin)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Kategori ekler (yönetici)",
    responses=error_responses(401, 403, 409, 422),
)
def create_category(data: CategoryCreate, _: AdminUser, db: DbSession) -> CategoryOut:
    return CategoryService(db).create(data)


@router.patch(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Kategoriyi günceller (yönetici)",
    responses=error_responses(400, 401, 403, 404, 409, 422),
)
def update_category(category_id: int, data: CategoryUpdate, _: AdminUser, db: DbSession) -> CategoryOut:
    return CategoryService(db).update(category_id, data)


@router.delete(
    "/{category_id}",
    response_model=DeleteResult,
    summary="Kategoriyi siler; bağlı kitap varsa pasifleştirir (yönetici)",
    responses=error_responses(401, 403, 404),
)
def delete_category(category_id: int, _: AdminUser, db: DbSession) -> DeleteResult:
    return CategoryService(db).delete(category_id)
