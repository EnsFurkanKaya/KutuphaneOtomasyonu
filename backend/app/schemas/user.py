"""Kullanıcı ve kimlik doğrulama şemaları."""
from datetime import datetime

from pydantic import Field

from app.domain.enums import Role
from app.schemas.common import ApiModel, EmailStrTR, OrmModel, StrongPassword


class UserOut(OrmModel):
    id: int
    student_number: str | None
    full_name: str
    email: str
    role: Role
    is_active: bool
    must_change_password: bool
    created_at: datetime


class UserSummary(OrmModel):
    id: int
    student_number: str | None
    full_name: str
    email: str


class RegisterRequest(ApiModel):
    student_number: str = Field(pattern=r"^\d{5,20}$", description="5-20 haneli öğrenci numarası")
    full_name: str = Field(min_length=3, max_length=120)
    email: EmailStrTR
    password: StrongPassword


class LoginRequest(ApiModel):
    email: EmailStrTR
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(ApiModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    user: UserOut


class UpdateMeRequest(ApiModel):
    full_name: str = Field(min_length=3, max_length=120)


class ChangePasswordRequest(ApiModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: StrongPassword


class AdminUserUpdate(ApiModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=120)
    is_active: bool | None = None
