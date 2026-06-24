import uuid
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.jwt import decode_token
from app.db.database import get_db
from app.db.models.user import UserSQL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserSQL:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.get(UserSQL, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception

    return user