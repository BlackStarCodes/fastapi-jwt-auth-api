#auth routes here. user can access user_routes only after being authenticated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from ..security import authenticate_user, create_access_token
from ..dependencies import session_dependency
from datetime import timedelta
from typing import Annotated
from ..schemas import Token
from ..config import TOKEN_EXPIRE_MINS


router = APIRouter()


@router.post("/login/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: session_dependency) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password!", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINS)
    access_token = create_access_token(data={"sub":str(user.id)}, expires_delta= access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
