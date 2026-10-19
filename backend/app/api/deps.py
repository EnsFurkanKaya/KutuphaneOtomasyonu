"""Ortak FastAPI bağımlılıkları: veritabanı oturumu, kimlik doğrulama ve rol kontrolleri.

Token iki yoldan kabul edilir:
  1. HttpOnly çerez (web arayüzü; JavaScript token'a erişemez)
  2. "Authorization: Bearer <token>" başlığı (Swagger, test ve API istemcileri)
"""
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.domain.enums import Role
from app.domain.errors import AuthenticationError, PermissionDeniedError
from app.models.user import User
from app.repositories.token_repository import TokenRepository

bearer_scheme = HTTPBearer(auto_error=False, description="Giriş yanıtındaki access_token değeri")

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    request: Request,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Kimliği doğrulanmış kullanıcıyı döndürür. Zorunlu parola değişikliği kontrolü yapmaz."""
    token = credentials.credentials if credentials else request.cookies.get(get_settings().cookie_name)
    if not token:
        raise AuthenticationError("Bu işlem için giriş yapmalısınız.", "OTURUM_YOK")
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError as exc:
        raise AuthenticationError("Oturumunuz geçersiz veya süresi dolmuş. Lütfen tekrar giriş yapın.", "OTURUM_GECERSIZ") from exc
    if TokenRepository(db).is_revoked(payload["jti"]):
        raise AuthenticationError("Oturum kapatılmış. Lütfen tekrar giriş yapın.", "OTURUM_KAPATILDI")
    try:
        user = db.get(User, int(payload["sub"]))
    except (TypeError, ValueError) as exc:
        raise AuthenticationError("Oturum geçersiz.", "OTURUM_GECERSIZ") from exc
    if user is None:
        raise AuthenticationError("Oturum geçersiz.", "OTURUM_GECERSIZ")
    request.state.token_payload = payload
    return user


def get_active_session_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Üretimde ilk kurulumda oluşturulan yönetici, parolasını değiştirmeden işlem yapamaz."""
    if user.must_change_password:
        raise PermissionDeniedError(
            "Devam etmeden önce parolanızı değiştirmeniz gerekiyor.", "PAROLA_DEGISIKLIGI_GEREKLI"
        )
    return user


def require_admin(user: Annotated[User, Depends(get_active_session_user)]) -> User:
    if user.role != Role.ADMIN.value:
        raise PermissionDeniedError("Bu işlem için yönetici yetkisi gereklidir.", "YONETICI_YETKISI_GEREKLI")
    return user


def require_student(user: Annotated[User, Depends(get_active_session_user)]) -> User:
    if user.role != Role.STUDENT.value:
        raise PermissionDeniedError("Bu işlem yalnızca öğrenciler içindir.", "SADECE_OGRENCI")
    return user


AuthenticatedUser = Annotated[User, Depends(get_current_user)]
CurrentUser = Annotated[User, Depends(get_active_session_user)]
AdminUser = Annotated[User, Depends(require_admin)]
StudentUser = Annotated[User, Depends(require_student)]
