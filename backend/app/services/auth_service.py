"""Kimlik doğrulama iş akışları: kayıt, giriş, çıkış."""
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    hash_password,
    password_needs_rehash,
    verify_dummy_password,
    verify_password,
)
from app.db.session import transaction
from app.domain.enums import Role
from app.domain.errors import AuthenticationError, ConflictError, TooManyAttemptsError
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import RegisterRequest

INVALID_CREDENTIALS = "E-posta adresi veya parola hatalı."


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)
        self.tokens = TokenRepository(session)
        self.settings = get_settings()

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("Bu e-posta adresiyle kayıtlı bir hesap zaten var.", "EPOSTA_KULLANIMDA")
        if self.users.get_by_student_number(data.student_number):
            raise ConflictError("Bu öğrenci numarasıyla kayıtlı bir hesap zaten var.", "OGRENCI_NO_KULLANIMDA")
        user = User(
            student_number=data.student_number,
            full_name=data.full_name,
            email=data.email,
            password_hash=hash_password(data.password),
            role=Role.STUDENT.value,
            is_active=True,
        )
        try:
            with transaction(self.session):
                self.users.add(user)
                self.session.flush()
        except IntegrityError as exc:  # eşzamanlı aynı kayıt denemesi
            raise ConflictError("E-posta veya öğrenci numarası zaten kullanımda.", "KAYIT_CAKISMASI") from exc
        return user

    def login(self, email: str, password: str) -> tuple[str, datetime, User]:
        """UML: User.login(). Başarısız denemeleri sayar, eşik aşılınca hesabı geçici kilitler."""
        now = utcnow()
        user = self.users.get_by_email(email)
        if user is None:
            verify_dummy_password(password)  # zamanlama farkıyla e-posta tespitini zorlaştırır
            raise AuthenticationError(INVALID_CREDENTIALS, "GECERSIZ_KIMLIK_BILGISI")

        if user.locked_until and user.locked_until > now:
            minutes = max(1, int((user.locked_until - now).total_seconds() // 60) + 1)
            raise TooManyAttemptsError(
                f"Çok fazla başarısız giriş denemesi. Lütfen yaklaşık {minutes} dakika sonra tekrar deneyin."
            )

        if not verify_password(user.password_hash, password):
            with transaction(self.session):
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= self.settings.max_failed_logins:
                    user.locked_until = now + timedelta(minutes=self.settings.login_lock_minutes)
                    user.failed_login_attempts = 0
            raise AuthenticationError(INVALID_CREDENTIALS, "GECERSIZ_KIMLIK_BILGISI")

        with transaction(self.session):
            user.failed_login_attempts = 0
            user.locked_until = None
            if password_needs_rehash(user.password_hash):
                user.password_hash = hash_password(password)
            self.tokens.purge_expired(now)

        token, _jti, expires_at = create_access_token(user.id, user.role)
        return token, expires_at, user

    def logout(self, jti: str, expires_at: datetime) -> None:
        """UML: User.logout(). Token kimliği iptal listesine eklenir; token tekrar kullanılamaz."""
        with transaction(self.session):
            self.tokens.revoke(jti, expires_at)
