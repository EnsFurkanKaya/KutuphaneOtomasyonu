"""Raporlama endpoint'leri (yalnızca yönetici)."""
from datetime import date

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, DbSession
from app.api.routers.docs import error_responses
from app.schemas.report import DashboardStats, OverdueReport
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Raporlar"])


@router.get(
    "/overdue",
    response_model=OverdueReport,
    summary="Gecikme raporu (yönetici)",
    description="İade edilmemiş ve son iade tarihi geçmiş kayıtlar. Tarih aralığı son iade tarihine uygulanır.",
    responses=error_responses(400, 401, 403, 422),
)
def overdue_report(
    _: AdminUser,
    db: DbSession,
    start_date: date | None = Query(None, description="Son iade tarihi başlangıcı (YYYY-AA-GG)"),
    end_date: date | None = Query(None, description="Son iade tarihi bitişi (YYYY-AA-GG)"),
    user_id: int | None = Query(None, gt=0),
    book_id: int | None = Query(None, gt=0),
    student: str | None = Query(None, max_length=100, description="Öğrenci adı veya numarası"),
    book: str | None = Query(None, max_length=100, description="Kitap adı veya ISBN"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> OverdueReport:
    return ReportService(db).overdue_report(
        start_date=start_date,
        end_date=end_date,
        user_id=user_id,
        book_id=book_id,
        student=student,
        book=book,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Yönetici paneli istatistikleri",
    responses=error_responses(401, 403),
)
def dashboard(_: AdminUser, db: DbSession) -> DashboardStats:
    return ReportService(db).dashboard()
