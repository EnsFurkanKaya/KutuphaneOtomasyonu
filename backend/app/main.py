"""FastAPI ana uygulama modülü.

CORS, OpenAPI şeması, hata işleyicileri ve router yapılandırması burada tanımlanır.
"""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.routers import api_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Başlangıç ve kapanış yaşam döngüsü kancaları
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Online Kütüphane Yönetim Sistemi - RESTful API Dokümantasyonu",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS yapılandırması
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# İstisna işleyicilerinin kaydedilmesi
register_exception_handlers(app)

# API router'ının dahil edilmesi
app.include_router(api_router)


@app.get("/health", tags=["Sağlık Durumu"], summary="Sistem sağlık kontrolü")
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
