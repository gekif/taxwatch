from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import User
from ..schemas import Token, UserCreate, UserOut
from ..security import create_access_token, hash_password, verify_password
from ..services import log_action

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Verified when the user does not exist, to keep response timing similar.
_DUMMY_HASH = hash_password("dummy-password")


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == form.username))
    ok = verify_password(form.password, user.password_hash if user else _DUMMY_HASH)
    if not user or not user.is_active or not ok:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    log_action(db, user.username, "login", "user", user.id)
    db.commit()
    return Token(
        access_token=create_access_token(user.username, user.role),
        username=user.username,
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
):
    if db.scalar(select(User).where(User.username == payload.username)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    user = User(
        username=payload.username,
        full_name=payload.full_name,
        role=payload.role,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    log_action(db, admin.username, "create", "user", user.id, f"role={user.role}")
    db.commit()
    return user
