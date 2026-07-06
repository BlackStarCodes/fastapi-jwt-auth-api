#all user endpoint should be here
from fastapi import APIRouter, HTTPException, Query, Depends,status
from ..dependencies import session_dependency
from ..schemas import UserOut, UserSignup, UserCreate
from ..models import UserORM
from sqlalchemy import select
from ..security import pwd_hashed, get_current_user
from typing import Annotated, List

router = APIRouter()


@router.post("/users/", response_model= UserOut)
async def new_user(user: UserSignup, session: session_dependency):
    if session.scalar((select(UserORM).where(UserORM.name == user.name))):
        raise HTTPException(status_code=409, detail="username already taken!")
    if session.scalar((select(UserORM).where(UserORM.email == user.email))):
        raise HTTPException(status_code=409, detail="email already in use!")
    db_user = UserORM(
        name = user.name,
        fullname = user.fullname,
        email = user.email,
        hashed_password = pwd_hashed(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get("/users/", response_model=List[UserOut])
async def read_users(
    session: session_dependency, 
    offset: int = 0, #just synonyms for start
    limit: Annotated[int, Query(le=100)] = 100,):
    users = session.scalars(select(UserORM).offset(offset).limit(limit)).all()
    return users


@router.get("/users/me", response_model=UserOut)
async def read_current_user(user:Annotated[UserCreate, Depends(get_current_user)]):
    return user


@router.get("/users/{user_id}", response_model=UserOut)
async def read_a_user(
    user_id: int,
    session: session_dependency,):
    user = session.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user


@router.delete("/users/{user_id}")
async def remove_user(
    user: Annotated[UserORM, Depends(get_current_user)],
    user_id: int,
    session: session_dependency
) :
    if user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not allowed to delete this user!")
    session.delete(user)
    session.commit()
    return {"status":f"successfully removed the user with user id:{user_id} !"}


@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user: Annotated[UserORM, Depends(get_current_user)],
    update_user: UserSignup,
    user_id: int,
    session: session_dependency
) :
    db_user = user
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    
    if user_id != db_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Not allowed to modify this user!")
    
    existing = session.scalar(select(UserORM).where(UserORM.name == update_user.name))
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail="username already taken, enter new username!")
    
    existing = session.scalar((select(UserORM).where(UserORM.email == update_user.email)))
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail="email already in use!, enter new email")
    
    db_user.name = update_user.name
    db_user.fullname = update_user.fullname
    db_user.email = update_user.email
    db_user.hashed_password = pwd_hashed(update_user.password)

    session.commit()
    session.refresh(db_user)
    return db_user