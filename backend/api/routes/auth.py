"""
Authentication
==============
Email + password accounts with bcrypt-hashed passwords and JWT sessions.

  POST /auth/signup   {email, username, password}  -> {token, user}
  POST /auth/login    {email, password}            -> {token, user}
  GET  /auth/me       (Bearer token)               -> user

Display name (username) is public; email is private (login only).
"""
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator

from db.session import get_db
from db.models import User
from api.routes.users import UserOut

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-insecure-secret-change-in-prod")
JWT_ALGO = "HS256"
TOKEN_TTL_DAYS = 30


# ── Schemas ───────────────────────────────────────────────────────────────────

class SignupIn(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _username_ok(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 24:
            raise ValueError("Username must be 2–24 characters")
        return v

    @field_validator("password")
    @classmethod
    def _password_ok(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class AuthOut(BaseModel):
    token: str
    user: UserOut


# ── Helpers ───────────────────────────────────────────────────────────────────

def _hash_pw(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_pw(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def _make_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_TTL_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: resolve the Bearer token to a User, or 401."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthOut, status_code=201)
def signup(data: SignupIn, db: Session = Depends(get_db)):
    email = data.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists. Try logging in.")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="That display name is taken. Pick another.")

    user = User(
        id=str(uuid.uuid4()),
        email=email,
        username=data.username,
        password_hash=_hash_pw(data.password),
        last_active=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return AuthOut(token=_make_token(user.id), user=UserOut.from_orm(user))


@router.post("/login", response_model=AuthOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    email = data.email.lower().strip()
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash or not _verify_pw(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password.")
    user.last_active = datetime.utcnow()
    db.commit()
    return AuthOut(token=_make_token(user.id), user=UserOut.from_orm(user))


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return UserOut.from_orm(current)
