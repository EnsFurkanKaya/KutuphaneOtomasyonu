"""Parola hash'leme (Argon2id) ve JWT üretimi/doğrulaması."""
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.core.config import get_settings

_hasher = PasswordHasher()  # Argon2id, güvenli varsayılan parametreler
# Kullanıcı bulunamadığında da hash doğrulaması yaparak zamanlama farkını azaltırız.
_DUMMY_HASH = _hasher.hash("zamanlama-saldirisina-karsi-sahte-parola")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def verify_dummy_password(password: str) -> None:
    verify_password(_DUMMY_HASH, password)


def password_needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def create_access_token(user_id: int, role: str) -> tuple[str, str, datetime]:
    """JWT üretir. (token, jti, son_gecerlilik) döndürür."""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    jti = uuid.uuid4().hex
    payload = {"sub": str(user_id), "role": role, "jti": jti, "iat": now, "exp": expires_at}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expires_at


def decode_access_token(token: str) -> dict:
    """Geçersiz veya süresi dolmuş token için jwt.PyJWTError fırlatır."""
    settings = get_settings()
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "jti", "exp", "iat"]},
    )
