"""Domain hataları. HTTP durum kodlarına eşleme API katmanında yapılır."""


class DomainError(Exception):
    default_code = "IS_KURALI_IHLALI"

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.default_code


class BusinessRuleError(DomainError):
    """Geçersiz iş kuralı isteği (ör. stok yok, limit aşıldı)."""
    default_code = "IS_KURALI_IHLALI"


class NotFoundError(DomainError):
    default_code = "KAYIT_BULUNAMADI"


class ConflictError(DomainError):
    """Çakışma veya tekrarlanan işlem (ör. aynı e-posta, ikinci iade)."""
    default_code = "CAKISMA"


class AuthenticationError(DomainError):
    default_code = "KIMLIK_DOGRULANAMADI"


class PermissionDeniedError(DomainError):
    default_code = "YETKI_YOK"


class TooManyAttemptsError(DomainError):
    default_code = "COK_FAZLA_DENEME"
