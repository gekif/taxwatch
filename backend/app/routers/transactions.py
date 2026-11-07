from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Taxpayer, Transaction, User
from ..schemas import Page, TransactionCreate, TransactionOut
from ..services import calculate_tax, detect_anomaly, log_action

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=Page[TransactionOut])
def list_transactions(
    taxpayer_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    flagged_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(Transaction)
    if taxpayer_id:
        stmt = stmt.where(Transaction.taxpayer_id == taxpayer_id)
    if date_from:
        stmt = stmt.where(Transaction.trx_date >= date_from)
    if date_to:
        stmt = stmt.where(Transaction.trx_date <= date_to)
    if flagged_only:
        stmt = stmt.where(Transaction.is_flagged.is_(True))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(
        stmt.options(selectinload(Transaction.taxpayer))
        .order_by(Transaction.trx_date.desc(), Transaction.id.desc())
        .offset(skip)
        .limit(limit)
    ).all()
    return {"total": total, "items": items}


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "officer")),
):
    tp = db.get(Taxpayer, payload.taxpayer_id)
    if tp is None or not tp.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Taxpayer not found")
    history = list(
        db.scalars(
            select(Transaction.amount)
            .where(Transaction.taxpayer_id == tp.id)
            .order_by(Transaction.id.desc())
            .limit(20)
        )
    )
    reason = detect_anomaly(payload.amount, settings.anomaly_threshold, history)
    trx = Transaction(
        taxpayer_id=tp.id,
        trx_date=payload.trx_date,
        amount=payload.amount,
        tax_amount=calculate_tax(tp.category, payload.amount),
        source=payload.source,
        is_flagged=reason is not None,
        flag_reason=reason,
        created_by=user.id,
    )
    db.add(trx)
    db.flush()
    log_action(db, user.username, "create", "transaction", trx.id, reason or "")
    db.commit()
    return trx


@router.post("/{trx_id}/clear-flag", response_model=TransactionOut)
def clear_flag(
    trx_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "auditor")),
):
    trx = db.get(Transaction, trx_id)
    if trx is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Transaction not found")
    if not trx.is_flagged:
        raise HTTPException(status.HTTP_409_CONFLICT, "Transaction is not flagged")
    log_action(db, user.username, "clear_flag", "transaction", trx.id, trx.flag_reason or "")
    trx.is_flagged = False
    trx.flag_reason = None
    db.commit()
    return trx
