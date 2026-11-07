from fastapi import APIRouter, Depends
from sqlalchemy import case, extract, func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Taxpayer, Transaction, User
from ..schemas import Summary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=Summary)
def summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    t = Transaction
    count, amount, tax, flagged = db.execute(
        select(
            func.count(t.id),
            func.coalesce(func.sum(t.amount), 0),
            func.coalesce(func.sum(t.tax_amount), 0),
            func.count(case((t.is_flagged.is_(True), 1))),
        )
    ).one()
    taxpayers = db.scalar(select(func.count(Taxpayer.id)).where(Taxpayer.is_active.is_(True)))

    by_category = [
        {"category": c, "transactions": int(n), "amount": int(a), "tax": int(x)}
        for c, n, a, x in db.execute(
            select(
                Taxpayer.category,
                func.count(t.id),
                func.coalesce(func.sum(t.amount), 0),
                func.coalesce(func.sum(t.tax_amount), 0),
            )
            .join(Taxpayer, Taxpayer.id == t.taxpayer_id)
            .group_by(Taxpayer.category)
            .order_by(Taxpayer.category)
        )
    ]

    year, month = extract("year", t.trx_date), extract("month", t.trx_date)
    rows = db.execute(
        select(year, month, func.sum(t.amount), func.sum(t.tax_amount))
        .group_by(year, month)
        .order_by(year.desc(), month.desc())
        .limit(6)
    ).all()
    monthly = [
        {"month": f"{int(y):04d}-{int(m):02d}", "amount": int(a), "tax": int(x)}
        for y, m, a, x in reversed(rows)
    ]
    return {
        "taxpayers": taxpayers,
        "transactions": count,
        "total_amount": int(amount),
        "total_tax": int(tax),
        "flagged": flagged,
        "by_category": by_category,
        "monthly": monthly,
    }
