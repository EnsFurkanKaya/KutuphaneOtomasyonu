"""Ortak şemalar ve yeniden kullanılabilir doğrulayıcılar."""
from typing import Annotated, Generic, TypeVar

from email_validator import EmailNotValidError, validate_email
from pydantic import AfterValidator, BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiModel(BaseModel):
    """Tüm istek şemaları için temel: bilinmeyen alanları reddeder, metinleri kırpar."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    pages: int = Field(ge=0)


class MessageResponse(BaseModel):
    message: str


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorResponse(BaseModel):
    error: ErrorBody


def normalize_email(value: str) -> str:
    try:
        result = validate_email(value.strip(), check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValueError("Geçerli bir e-posta adresi giriniz.") from exc
    return result.normalized.lower()


def validate_password_strength(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Parola en az 8 karakter olmalıdır.")
    if len(value) > 128:
        raise ValueError("Parola en fazla 128 karakter olabilir.")
    if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
        raise ValueError("Parola en az bir harf ve bir rakam içermelidir.")
    return value


EmailStrTR = Annotated[str, Field(max_length=254), AfterValidator(normalize_email)]
StrongPassword = Annotated[str, AfterValidator(validate_password_strength)]


def make_page(items: list, total: int, page: int, page_size: int) -> dict:
    pages = (total + page_size - 1) // page_size if total else 0
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}
