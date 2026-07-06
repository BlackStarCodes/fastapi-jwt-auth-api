import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from .dependencies import session_dependency, oauth2_scheme
from .models import UserORM
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from typing import Annotated
from .schemas import TokenData
from .config import SECRET_KEY, ALGO



hasher = PasswordHash.recommended()
dummy = hasher.hash("dummy-pass")


def pwd_hashed(pwd):
    return hasher.hash(pwd)


def verify_pass(pwd, hashed_pwd):
    return hasher.verify(pwd, hashed_pwd)


def authenticate_user(session: session_dependency, username: str, password: str):
    user = session.scalar(select(UserORM).where(UserORM.name == username))
    if not user:
        verify_pass(password, dummy)
        return False
    if not verify_pass(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGO)
    return encoded_jwt
    

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: session_dependency):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials!", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGO])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = session.scalar((select(UserORM).where(UserORM.name == token_data.username)))
    if user is None:
        raise credentials_exception
    return user