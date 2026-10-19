"""Kitap endpoint'leri."""
from fastapi import APIRouter, Query, status

from app.api.deps import AdminUser, CurrentUser, DbSession
from app.api.routers.docs import error_responses
from app.schemas.book import BookCreate, BookOut, BookSortField, BookUpdate, DeleteResult, SortOrder, StockUpdate
from app.schemas.common import Page
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["Kitaplar"])


@router.get(
    "",
    response_model=Page[BookOut],
    summary="Kitapları arar, filtreler, sıralar ve sayfalar",
    responses=error_responses(401, 422),
)
def list_books(
    user: CurrentUser,
    db: DbSession,
    q: str | None = Query(None, max_length=100, description="Kitap adı, yazar, ISBN veya kategori adında arar"),
    title: str | None = Query(None, max_length=100),
    author: str | None = Query(None, max_length=100),
    isbn: str | None = Query(None, max_length=20),
    category_id: int | None = Query(None, gt=0),
    available_only: bool = Query(False, description="Yalnızca stokta olan kitaplar"),
    include_inactive: bool = Query(False, description="Pasif kitapları da getir (yalnızca yönetici)"),
    sort: BookSortField = "title",
    order: SortOrder = "asc",
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
) -> dict:
    return BookService(db).search_books(
        q=q,
        title=title,
        author=author,
        isbn=isbn,
        category_id=category_id,
        available_only=available_only,
        include_inactive=include_inactive and user.is_admin,
        sort=sort,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get("/{book_id}", response_model=BookOut, summary="Kitap ayrıntısı", responses=error_responses(401, 404))
def get_book(book_id: int, user: CurrentUser, db: DbSession) -> BookOut:
    return BookOut.model_validate(BookService(db).get_book(book_id, include_inactive=user.is_admin))


@router.post(
    "",
    response_model=BookOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kitap ekler (yönetici)",
    responses=error_responses(400, 401, 403, 404, 409, 422),
)
def create_book(data: BookCreate, _: AdminUser, db: DbSession) -> BookOut:
    return BookOut.model_validate(BookService(db).create(data))


@router.patch(
    "/{book_id}",
    response_model=BookOut,
    summary="Kitap bilgilerini günceller (yönetici)",
    responses=error_responses(400, 401, 403, 404, 409, 422),
)
def update_book(book_id: int, data: BookUpdate, _: AdminUser, db: DbSession) -> BookOut:
    return BookOut.model_validate(BookService(db).update(book_id, data))


@router.patch(
    "/{book_id}/stock",
    response_model=BookOut,
    summary="Toplam kopya sayısını günceller; mevcut kopya otomatik hesaplanır (yönetici)",
    responses=error_responses(400, 401, 403, 404, 422),
)
def update_stock(book_id: int, data: StockUpdate, _: AdminUser, db: DbSession) -> BookOut:
    return BookOut.model_validate(BookService(db).update_stock(book_id, data.total_copies))


@router.delete(
    "/{book_id}",
    response_model=DeleteResult,
    summary="Kitabı siler; ödünç geçmişi varsa pasifleştirir (yönetici)",
    responses=error_responses(401, 403, 404),
)
def delete_book(book_id: int, _: AdminUser, db: DbSession) -> DeleteResult:
    return BookService(db).delete(book_id)
