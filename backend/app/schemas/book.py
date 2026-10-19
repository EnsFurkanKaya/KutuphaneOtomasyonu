"""Kitap şemaları."""
import re
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import AfterValidator, Field, computed_field, model_validator

from app.domain.enums import DeleteAction
from app.schemas.category import CategorySummary
from app.schemas.common import ApiModel, OrmModel

_ISBN_RE = re.compile(r"^(\d{9}[\dX]|\d{13})$")


def normalize_isbn(value: str) -> str:
    """Tire ve boşlukları kaldırır; 10 veya 13 haneli biçimi doğrular."""
    cleaned = re.sub(r"[\s-]", "", value).upper()
    if not _ISBN_RE.fullmatch(cleaned):
        raise ValueError("ISBN 10 veya 13 haneli olmalıdır (tire ve boşluk kullanılabilir).")
    return cleaned


def validate_publication_year(value: int | None) -> int | None:
    if value is None:
        return value
    if value < 1450 or value > date.today().year + 1:
        raise ValueError(f"Yayın yılı 1450 ile {date.today().year + 1} arasında olmalıdır.")
    return value


Isbn = Annotated[str, Field(max_length=20), AfterValidator(normalize_isbn)]
PublicationYear = Annotated[int | None, AfterValidator(validate_publication_year)]


class BookBase(ApiModel):
    isbn: Isbn
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    publisher: str | None = Field(default=None, max_length=160)
    publication_year: PublicationYear = None
    category_id: int | None = Field(default=None, gt=0)
    shelf_location: str | None = Field(default=None, max_length=40)


class BookCreate(BookBase):
    total_copies: int = Field(ge=0, le=10_000)


class BookUpdate(ApiModel):
    isbn: Isbn | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    publisher: str | None = Field(default=None, max_length=160)
    publication_year: PublicationYear = None
    category_id: int | None = Field(default=None, gt=0)
    shelf_location: str | None = Field(default=None, max_length=40)
    is_active: bool | None = None

    @model_validator(mode="after")
    def _required_not_null(self) -> "BookUpdate":
        for field in ("isbn", "title", "author", "is_active"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"'{field}' alanı boş bırakılamaz.")
        return self


class StockUpdate(ApiModel):
    total_copies: int = Field(ge=0, le=10_000)


class BookOut(OrmModel):
    id: int
    isbn: str
    title: str
    author: str
    description: str | None
    publisher: str | None
    publication_year: int | None
    category_id: int | None
    category: CategorySummary | None
    shelf_location: str | None
    total_copies: int
    available_copies: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_available(self) -> bool:
        return self.is_active and self.available_copies > 0


class BookSummary(OrmModel):
    id: int
    isbn: str
    title: str
    author: str


class DeleteResult(ApiModel):
    id: int
    action: DeleteAction
    message: str


BookSortField = Literal["title", "author", "publication_year", "created_at", "available_copies"]
SortOrder = Literal["asc", "desc"]
