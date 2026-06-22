import uuid
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import hash_password, verify_password
from app.db.database import get_db
from app.db.models.user import UserSQL, UserRole
from app.schemas.user import RefreshRequest, TokenPair, UserLogin, UserRead, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, db: Session = Depends(get_db)) -> UserSQL:
    hashed_pw = await hash_password(payload.password)

    user = UserSQL(
        email=payload.email,
        hashed_password=hashed_pw,
        role=UserRole.RECRUITER,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    user = db.query(UserSQL).filter(UserSQL.email == payload.email).first()

    if user is None or not await verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    return TokenPair(
        access_token=create_access_token(user.id, user.role.value, email=user.email),
        refresh_token=create_refresh_token(user.id, user.role.value, email=user.email),
    )

@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )

    try:
        decoded = decode_token(payload.refresh_token)
    except jwt.PyJWTError:
        raise credentials_exception

    if decoded.get("type") != "refresh":
        raise credentials_exception

    user = db.get(UserSQL, uuid.UUID(decoded["sub"]))
    if user is None or not user.is_active:
        raise credentials_exception

    return TokenPair(
        access_token=create_access_token(user.id, user.role.value, email=user.email),
        refresh_token=create_refresh_token(user.id, user.role.value, email=user.email),
    )

@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: UserSQL = Depends(get_current_user)) -> UserSQL:
    return current_user