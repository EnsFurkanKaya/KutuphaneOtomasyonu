"""HTTP router'ları."""
from fastapi import APIRouter

from app.api.routers import auth, books, categories, loans, reports, users

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(books.router)
api_router.include_router(categories.router)
api_router.include_router(users.router)
api_router.include_router(loans.router)
api_router.include_router(reports.router)
