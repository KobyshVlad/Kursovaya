from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    start_month: date


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    start_month: date
    created_at: datetime
    updated_at: datetime


class UserUpdateRequest(BaseModel):
    name: str
    email: EmailStr
    start_month: date


class CategoryCreateRequest(BaseModel):
    name: str


class CategoryUpdateRequest(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    created_at: datetime
    updated_at: datetime


class OperationCreateRequest(BaseModel):
    category_id: int
    type: str
    amount: Decimal
    operation_date: date
    comment: str | None = None


class OperationUpdateRequest(BaseModel):
    category_id: int
    type: str
    amount: Decimal
    operation_date: date
    comment: str | None = None


class OperationResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    category_name: str | None = None
    type: str
    amount: Decimal
    operation_date: date
    comment: str | None = None
    created_at: datetime
    updated_at: datetime


class BudgetCreateRequest(BaseModel):
    category_id: int
    month: int
    year: int
    planned_amount: Decimal


class BudgetUpdateRequest(BaseModel):
    planned_amount: Decimal


class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    category_name: str | None = None
    month: int
    year: int
    planned_amount: Decimal
    created_at: datetime
    updated_at: datetime


class BudgetCompareResponse(BaseModel):
    category_id: int
    category_name: str
    month: int
    year: int
    planned_amount: Decimal
    actual_amount: Decimal
    difference: Decimal
