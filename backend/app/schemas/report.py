"""Raporlama şemaları."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class OverdueItem(BaseModel):
    loan_id: int
    user_id: int
    student_number: str | None
    full_name: str
    email: str
    book_id: int
    book_title: str
    isbn: str
    borrowed_at: datetime
    due_at: datetime
    overdue_days: int = Field(ge=0)


class OverdueReport(BaseModel):
    items: list[OverdueItem]
    total: int
    page: int
    page_size: int
    pages: int
    generated_at: datetime
    start_date: date | None
    end_date: date | None


class ActivityItem(BaseModel):
    loan_id: int
    type: Literal["BORROW", "RETURN"]
    occurred_at: datetime
    student_number: str | None
    full_name: str
    book_title: str


class DashboardStats(BaseModel):
    active_book_titles: int
    total_copies: int
    available_copies: int
    active_loans: int
    overdue_loans: int
    active_students: int
    total_categories: int
    recent_activity: list[ActivityItem]
    generated_at: datetime
