"""Tutarlı JSON hata biçimi ve istisna işleyicileri.

Tüm hatalar şu biçimde döner:
    {"error": {"code": "...", "message": "...", "details": [{"field": "...", "message": "..."}]}}
"""
import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.domain.errors import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    DomainError,
    NotFoundError,
    PermissionDeniedError,
    TooManyAttemptsError,
)

logger = logging.getLogger("kutuphane")

DOMAIN_STATUS: list[tuple[type[DomainError], int]] = [
    (AuthenticationError, status.HTTP_401_UNAUTHORIZED),
    (PermissionDeniedError, status.HTTP_403_FORBIDDEN),
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ConflictError, status.HTTP_409_CONFLICT),
    (TooManyAttemptsError, status.HTTP_429_TOO_MANY_REQUESTS),
    (BusinessRuleError, status.HTTP_400_BAD_REQUEST),
]

HTTP_MESSAGES = {
    400: ("GECERSIZ_ISTEK", "İstek geçersiz."),
    401: ("KIMLIK_DOGRULANAMADI", "Bu işlem için giriş yapmalısınız."),
    403: ("YETKI_YOK", "Bu işlem için yetkiniz yok."),
    404: ("KAYNAK_BULUNAMADI", "İstenen kaynak bulunamadı."),
    405: ("METOT_DESTEKLENMIYOR", "Bu HTTP metodu bu adreste desteklenmiyor."),
}

VALIDATION_MESSAGES = {
    "missing": "Bu alan zorunludur.",
    "string_type": "Metin değeri olmalıdır.",
    "int_type": "Tam sayı olmalıdır.",
    "int_parsing": "Geçerli bir tam sayı olmalıdır.",
    "int_from_float": "Tam sayı olmalıdır.",
    "bool_type": "true veya false olmalıdır.",
    "bool_parsing": "true veya false olmalıdır.",
    "date_parsing": "Geçerli bir tarih olmalıdır (YYYY-AA-GG).",
    "date_from_datetime_parsing": "Geçerli bir tarih olmalıdır (YYYY-AA-GG).",
    "date_type": "Geçerli bir tarih olmalıdır (YYYY-AA-GG).",
    "json_invalid": "İstek gövdesi geçerli bir JSON değil.",
    "model_attributes_type": "İstek gövdesi geçerli bir JSON nesnesi olmalıdır.",
    "dict_type": "İstek gövdesi geçerli bir JSON nesnesi olmalıdır.",
    "extra_forbidden": "Bu alana izin verilmiyor.",
    "string_pattern_mismatch": "Değer beklenen biçimde değil.",
    "enum": "İzin verilen değerlerden biri olmalıdır.",
    "literal_error": "İzin verilen değerlerden biri olmalıdır.",
}


def error_body(code: str, message: str, details: list[dict] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


def _translate(err: dict) -> str:
    etype = err.get("type", "")
    ctx = err.get("ctx") or {}
    if etype == "string_too_short":
        return f"En az {ctx.get('min_length')} karakter olmalıdır."
    if etype == "string_too_long":
        return f"En fazla {ctx.get('max_length')} karakter olabilir."
    if etype == "greater_than_equal":
        return f"{ctx.get('ge')} veya daha büyük olmalıdır."
    if etype == "greater_than":
        return f"{ctx.get('gt')} değerinden büyük olmalıdır."
    if etype == "less_than_equal":
        return f"{ctx.get('le')} veya daha küçük olmalıdır."
    if etype == "less_than":
        return f"{ctx.get('lt')} değerinden küçük olmalıdır."
    if etype in ("literal_error", "enum") and ctx.get("expected"):
        return f"İzin verilen değerler: {ctx.get('expected')}."
    if etype == "value_error":
        # Kendi doğrulayıcılarımız Türkçe ValueError mesajı üretir.
        error = ctx.get("error")
        return str(error) if error else "Geçersiz değer."
    if etype == "string_pattern_mismatch" and err.get("loc", [])[-1:] == ("student_number",):
        return "Öğrenci numarası 5-20 haneli rakamlardan oluşmalıdır."
    return VALIDATION_MESSAGES.get(etype, "Geçersiz değer.")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        status_code = next((code for cls, code in DOMAIN_STATUS if isinstance(exc, cls)), 400)
        headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
        return JSONResponse(status_code=status_code, content=error_body(exc.code, exc.message), headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for err in exc.errors():
            loc = [str(p) for p in err.get("loc", ()) if p not in ("body", "query", "path")]
            details.append({"field": ".".join(loc) or None, "message": _translate(err)})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_body("DOGRULAMA_HATASI", "Gönderilen veriler geçersiz.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code, message = HTTP_MESSAGES.get(exc.status_code, ("HTTP_HATASI", "İstek işlenemedi."))
        if isinstance(exc.detail, str) and exc.status_code not in HTTP_MESSAGES:
            message = exc.detail
        return JSONResponse(status_code=exc.status_code, content=error_body(code, message))

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Ayrıntı yalnızca sunucu loglarına yazılır; istek gövdesi (parolalar) loglanmaz.
        logger.exception("Beklenmeyen hata: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_body("SUNUCU_HATASI", "Beklenmeyen bir hata oluştu. Lütfen daha sonra tekrar deneyin."),
        )
