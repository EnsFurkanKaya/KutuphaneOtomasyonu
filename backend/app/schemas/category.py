"""Kategori şemaları."""
from datetime import datetime

from pydantic import Field

from app.schemas.common import ApiModel, OrmModel


class CategoryCreate(ApiModel):
    name: str = Field(min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(ApiModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class CategorySummary(OrmModel):
    id: int
    name: str


class CategoryOut(OrmModel):
    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    book_count: int = 0
