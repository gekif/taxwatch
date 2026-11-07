from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Taxpayer, User
from ..schemas import Page, TaxpayerCreate, TaxpayerOut, TaxpayerUpdate
from ..services import log_action

router = APIRouter(prefix="/api/taxpayers", tags=["taxpayers"])


def _get_active(db: Session, taxpayer_id: int) -> Taxpayer:
    tp = db.get(Taxpayer, taxpayer_id)
    if tp is None or not tp.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Taxpayer not found")
    return tp


@router.get("", response_model=Page[TaxpayerOut])
def list_taxpayers(
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(Taxpayer).where(Taxpayer.is_active.is_(True))
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Taxpayer.name.ilike(like), Taxpayer.npwpd.ilike(like)))
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    items = db.scalars(stmt.order_by(Taxpayer.name).offset(skip).limit(limit)).all()
    return {"total": total, "items": items}


@router.post("", response_model=TaxpayerOut, status_code=201)
def create_taxpayer(
    payload: TaxpayerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "officer")),
):
    if db.scalar(select(Taxpayer).where(Taxpayer.npwpd == payload.npwpd)):
        raise HTTPException(status.HTTP_409_CONFLICT, "NPWPD already registered")
    tp = Taxpayer(**payload.model_dump())
    db.add(tp)
    db.flush()
    log_action(db, user.username, "create", "taxpayer", tp.id, tp.npwpd)
    db.commit()
    return tp


@router.get("/{taxpayer_id}", response_model=TaxpayerOut)
def get_taxpayer(
    taxpayer_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return _get_active(db, taxpayer_id)


@router.put("/{taxpayer_id}", response_model=TaxpayerOut)
def update_taxpayer(
    taxpayer_id: int,
    payload: TaxpayerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "officer")),
):
    tp = _get_active(db, taxpayer_id)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(tp, key, value)
    log_action(db, user.username, "update", "taxpayer", tp.id, ",".join(changes))
    db.commit()
    return tp


@router.delete("/{taxpayer_id}", status_code=204)
def delete_taxpayer(
    taxpayer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin")),
):
    """Soft delete: transactions keep referencing the taxpayer for audit purposes."""
    tp = _get_active(db, taxpayer_id)
    tp.is_active = False
    log_action(db, user.username, "delete", "taxpayer", tp.id, tp.npwpd)
    db.commit()
