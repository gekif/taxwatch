from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import AuditLog, User
from ..schemas import AuditOut, Page

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("", response_model=Page[AuditOut])
def list_audit(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("admin", "auditor")),
):
    total = db.scalar(select(func.count(AuditLog.id)))
    items = db.scalars(
        select(AuditLog).order_by(AuditLog.id.desc()).offset(skip).limit(limit)
    ).all()
    return {"total": total, "items": items}
