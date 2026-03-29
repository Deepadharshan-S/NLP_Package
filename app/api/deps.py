from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_access_token
from app.models.user import User
from app.db.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔥 IMPORTANT: allow missing header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    auto_error=False
)


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = None

    if token:
        payload = verify_access_token(token)

    # Fallback to cookie
    if not payload:
        cookie_token = request.cookies.get("access_token")
        if cookie_token:
            payload = verify_access_token(cookie_token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = int(payload.get("sub"))

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user