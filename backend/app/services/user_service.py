"""Kullanıcı profili ve yönetici kullanıcı yönetimi iş akışları."""
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import transaction
from app.domain.enums import Role
from app.domain.errors import BusinessRuleError, NotFoundError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.common import make_page
from app.schemas.user import AdminUserUpdate, ChangePasswordRequest, UpdateMeRequest, UserOut


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def update_me(self, user: User, data: UpdateMeRequest) -> User:
        """Öğrenci yalnızca ad soyad bilgisini güncelleyebilir; e-posta, numara ve rol değiştirilemez."""
        with transaction(self.session):
            user.full_name = data.full_name
        return user

    def change_password(self, user: User, data: ChangePasswordRequest) -> None:
        if not verify_password(user.password_hash, data.current_password):
            raise BusinessRuleError("Mevcut parola hatalı.", "MEVCUT_PAROLA_HATALI")
        if verify_password(user.password_hash, data.new_password):
            raise BusinessRuleError("Yeni parola mevcut paroladan farklı olmalıdır.", "AYNI_PAROLA")
        with transaction(self.session):
            user.password_hash = hash_password(data.new_password)
            user.must_change_password = False

    def list_users(
        self, *, q: str | None, role: Role | None, is_active: bool | None, page: int, page_size: int
    ) -> dict:
        items, total = self.users.list(
            q=q, role=role, is_active=is_active, offset=(page - 1) * page_size, limit=page_size
        )
        return make_page([UserOut.model_validate(u) for u in items], total, page, page_size)

    def get_user(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("Kullanıcı bulunamadı.")
        return user

    def admin_update(self, actor: User, user_id: int, data: AdminUserUpdate) -> User:
        user = self.get_user(user_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("is_active") is False and user.id == actor.id:
            raise BusinessRuleError("Kendi yönetici hesabınızı pasifleştiremezsiniz.", "KENDINI_PASIFLESTIREMEZ")
        if "full_name" in changes and changes["full_name"] is None:
            raise BusinessRuleError("Ad soyad boş bırakılamaz.", "ZORUNLU_ALAN")
        with transaction(self.session):
            for field, value in changes.items():
                if value is not None:
                    setattr(user, field, value)
        return user
