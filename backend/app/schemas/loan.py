"""Ödünç kaydı şemaları."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.enums import LoanStatus
from app.schemas.book import BookSummary
from app.schemas.common import ApiModel
from app.schemas.user import UserSummary


class LoanCreate(ApiModel):
    book_id: int = Field(gt=0)


class LoanOut(BaseModel):
    id: int
    user: UserSummary
    book: BookSummary
    borrowed_at: datetime
    due_at: datetime
    returned_at: datetime | None
    status: LoanStatus
    is_overdue: bool
    overdue_days: int = Field(ge=0)
    late_return_days: int = Field(ge=0)


LoanStatusFilter = Literal["active", "overdue", "returned", "all"]
