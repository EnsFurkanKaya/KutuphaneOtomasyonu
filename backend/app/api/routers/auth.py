"""Kimlik doğrulama endpoint'leri."""
from datetime import datetime, timezone

from fastapi import APIRouter, Request, Response, status

from app.api.deps import AuthenticatedUser, DbSession
from app.api.routers.docs import AUTH_ERRORS, VALIDATION_ERRORS, error_responses
from app.core.config import get_settings
from app.schemas.common import MessageResponse
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni öğrenci hesabı oluşturur",
    responses=error_responses(409, 422),
)
def register(data: RegisterRequest, db: DbSession) -> UserOut:
    user = AuthService(db).register(data)
    return UserOut.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Giriş yapar; HttpOnly oturum çerezi ve Bearer token döndürür",
    responses=error_responses(401, 422, 429),
)
def login(data: LoginRequest, response: Response, db: DbSession) -> TokenResponse:
    settings = get_settings()
    token, expires_at, user = AuthService(db).login(data.email, data.password)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/api",
    )
    return TokenResponse(access_token=token, expires_at=expires_at, user=UserOut.model_validate(user))


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Oturumu güvenli biçimde kapatır (token iptal edilir)",
    responses=AUTH_ERRORS,
)
def logout(request: Request, response: Response, user: AuthenticatedUser, db: DbSession) -> MessageResponse:
    payload = request.state.token_payload
    AuthService(db).logout(payload["jti"], datetime.fromtimestamp(payload["exp"], tz=timezone.utc))
    response.delete_cookie(get_settings().cookie_name, path="/api")
    return MessageResponse(message="Oturum güvenli şekilde kapatıldı.")


@router.get("/me", response_model=UserOut, summary="Oturum açmış kullanıcıyı döndürür", responses=AUTH_ERRORS)
def me(user: AuthenticatedUser) -> UserOut:
    return UserOut.model_validate(user)


__all__ = ["router", "VALIDATION_ERRORS"]
