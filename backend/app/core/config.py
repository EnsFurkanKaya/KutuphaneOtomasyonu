"""Uygulama yapılandırması.

Tüm yapılandırılabilir değerler (iş kuralı parametreleri dahil) ortam
değişkenlerinden okunur. Gizli bilgiler koda yazılmaz.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET_KEY = "yalnizca-gelistirme-icin-guvensiz-anahtar-degistirin-0123456789"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Online Kütüphane Yönetim Sistemi"
    app_env: Literal["development", "test", "production"] = "development"
    debug: bool = False

    database_url: str = "postgresql+psycopg://kutuphane:kutuphane@localhost:5432/kutuphane"

    # Kimlik doğrulama
    secret_key: str = DEV_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=60, ge=5, le=1440)
    cookie_name: str = "kutuphane_oturum"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "strict"

    # Parola denemesi koruması
    max_failed_logins: int = Field(default=5, ge=1, le=50)
    login_lock_minutes: int = Field(default=15, ge=1, le=1440)

    # CORS (virgülle ayrılmış kaynak listesi)
    cors_origins: str = "http://localhost:8080,http://localhost:5173"

    # İş kuralları
    loan_period_days: int = Field(default=14, ge=1, le=120)
    max_active_loans: int = Field(default=3, ge=1, le=20)
    app_timezone: str = "Europe/Istanbul"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @model_validator(mode="after")
    def _validate_production(self) -> "Settings":
        if self.app_env == "production":
            if self.debug:
                raise ValueError("Üretim ortamında DEBUG kapalı olmalıdır.")
            if self.secret_key == DEV_SECRET_KEY or len(self.secret_key) < 32:
                raise ValueError("Üretim ortamında en az 32 karakterlik benzersiz bir SECRET_KEY tanımlanmalıdır.")
            if not self.cookie_secure:
                raise ValueError("Üretim ortamında COOKIE_SECURE=true olmalıdır (HTTPS).")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
