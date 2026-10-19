"""OpenAPI dokümantasyonu için ortak hata yanıtı tanımları."""
from app.schemas.common import ErrorResponse

DESCRIPTIONS = {
    400: "Geçersiz iş kuralı isteği",
    401: "Kimlik doğrulaması yok veya geçersiz",
    403: "Yetki yok",
    404: "Kayıt bulunamadı",
    409: "Çakışma veya tekrarlanan işlem",
    422: "Doğrulama hatası",
    429: "Çok fazla başarısız giriş denemesi",
}


def error_responses(*codes: int) -> dict:
    return {code: {"model": ErrorResponse, "description": DESCRIPTIONS[code]} for code in codes}


AUTH_ERRORS = error_responses(401, 403)
VALIDATION_ERRORS = error_responses(422)
