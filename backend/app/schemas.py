from datetime import date, datetime, timedelta
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

Role = Literal["admin", "officer", "auditor"]
Category = Literal["hotel", "restoran", "hiburan", "parkir"]
T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    items: list[T]


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: Role
    full_name: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-z0-9_.]+$")
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role: Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str
    role: Role
    is_active: bool


class TaxpayerCreate(BaseModel):
    npwpd: str = Field(pattern=r"^[A-Z0-9]{6,20}$")
    name: str = Field(min_length=2, max_length=150)
    address: str = Field(default="", max_length=255)
    category: Category


class TaxpayerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    category: Category | None = None


class TaxpayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    npwpd: str
    name: str
    address: str
    category: Category
    is_active: bool


class TransactionCreate(BaseModel):
    taxpayer_id: int
    trx_date: date
    amount: int = Field(gt=0, le=10_000_000_000)
    source: Literal["tapping_box", "manual"] = "tapping_box"

    @field_validator("trx_date")
    @classmethod
    def not_in_future(cls, v: date) -> date:
        # One day of tolerance so users ahead of the server's time zone (e.g. WIB vs UTC)
        # can record "today" during the first hours of their day.
        if v > date.today() + timedelta(days=1):
            raise ValueError("trx_date cannot be in the future")
        return v


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    taxpayer_id: int
    taxpayer_name: str
    trx_date: date
    amount: int
    tax_amount: int
    source: str
    is_flagged: bool
    flag_reason: str | None


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor: str
    action: str
    entity: str
    entity_id: int | None
    detail: str
    created_at: datetime


class CategoryTotal(BaseModel):
    category: str
    transactions: int
    amount: int
    tax: int


class MonthTotal(BaseModel):
    month: str
    amount: int
    tax: int


class Summary(BaseModel):
    taxpayers: int
    transactions: int
    total_amount: int
    total_tax: int
    flagged: int
    by_category: list[CategoryTotal]
    monthly: list[MonthTotal]
