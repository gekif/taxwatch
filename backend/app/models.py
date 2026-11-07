from datetime import UTC, date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # admin | officer | auditor
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Taxpayer(Base):
    __tablename__ = "taxpayers"

    id: Mapped[int] = mapped_column(primary_key=True)
    npwpd: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    address: Mapped[str] = mapped_column(String(255), default="")
    category: Mapped[str] = mapped_column(String(20))  # hotel | restoran | hiburan | parkir
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (Index("ix_transactions_taxpayer_date", "taxpayer_id", "trx_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    taxpayer_id: Mapped[int] = mapped_column(ForeignKey("taxpayers.id"), index=True)
    trx_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[int] = mapped_column(BigInteger)  # IDR, whole rupiah
    tax_amount: Mapped[int] = mapped_column(BigInteger)
    source: Mapped[str] = mapped_column(String(20), default="tapping_box")
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    flag_reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    taxpayer: Mapped[Taxpayer] = relationship()

    @property
    def taxpayer_name(self) -> str:
        return self.taxpayer.name if self.taxpayer else ""


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(50))  # denormalised: survives user changes
    action: Mapped[str] = mapped_column(String(50), index=True)
    entity: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detail: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
