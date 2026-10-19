"""İptal edilmiş JWT kimlikleri (çıkış yapılmış oturumlar) veri erişimi."""
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


class TokenRepository:
    def __init__(self, session: Session):
        self.session = session

    def revoke(self, jti: str, expires_at: datetime) -> None:
        stmt = insert(RevokedToken).values(jti=jti, expires_at=expires_at).on_conflict_do_nothing()
        self.session.execute(stmt)

    def is_revoked(self, jti: str) -> bool:
        return self.session.execute(select(RevokedToken.jti).where(RevokedToken.jti == jti)).first() is not None

    def purge_expired(self, now: datetime) -> None:
        self.session.execute(delete(RevokedToken).where(RevokedToken.expires_at < now))
