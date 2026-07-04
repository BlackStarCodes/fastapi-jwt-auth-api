from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Annotated
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session
from dotenv import dotenv_values
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


class Base(DeclarativeBase):
    pass 


class User(Base):
    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String(50))
    hashed_password: Mapped[str] = mapped_column(String(100))


v = dotenv_values(".env")

user = v["user"]
pin = v["pin"]
host = v["host"]
port = v["port"]
db_name = v["db_name"]

db_url = f"postgresql+psycopg2://{user}:{pin}@{host}:{port}/{db_name}"
engine = create_engine(db_url) #engine just connection to db server

def create_table():
    Base.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session


session_dependency = Annotated[Session, Depends(get_session)]
create_table()

app = FastAPI()


class UserCreate(BaseModel):
    id: int | None = None
    name: str
    fullname: str | None = None
    email: str
    password: str 
    

class UserInDB(UserCreate):
    password: str
#plain password gonna be username + first 2 letter of email. changing user info may cause problem since you can deduce plain password anymore


hash = PasswordHash.recommended()
dummy = hash.hash("dummy-pass")


def get_pass_hash(pwd):
    return hash.hash(pwd)


def verify_pass(pwd, hashed_pwd):
    return hash.verify(pwd, hashed_pwd)


@app.post("/users/")
async def new_user(user: UserCreate, session: session_dependency):
    db_user = User(
        name = user.name,
        fullname = user.fullname,
        email = user.email,
        hashed_password = get_pass_hash(user.password)
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {db_user}


@app.post("/login/")
async def sign_in(username: str, password: str, session: session_dependency):
    user = session.scalar(select(User).where(User.name == username))
    if not user:
        verify_pass(password, dummy)
        raise HTTPException(status_code=401, detail="wrong credentials!")
    
    if not verify_pass(password,user.hashed_password):
        raise HTTPException(status_code=401, detail="wrong credentials!")
    return {"message": "signed in"}



@app.get("/users/", response_model=List[UserCreate])
async def read_users(
    session: session_dependency, 
    offset: int = 0, #just synonyms for start
    limit: Annotated[int, Query(le=100)] = 100,) -> List[UserCreate]:
    users = session.scalars(select(User).offset(offset).limit(limit)).all()
    return users


@app.get("/users/{user_id}")
async def read_a_user(
    user_id: int,
    session: session_dependency,) -> UserCreate:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user


@app.delete("/users/{user_id}")
async def remove_user(
    user_id: int,
    session: session_dependency
) -> UserCreate:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(user)
    session.commit()
    return {"status":"successfully removed!"}


@app.put("/users/{user_id}")
async def update_user(
    user: UserCreate,
    user_id: int,
    session: session_dependency
) -> UserCreate:
    db_user = session.get(User, user_id)
    db_user.name = user.name
    db_user.fullname = user.fullname
    db_user.email = user.email
    session.commit()
    session.refresh(db_user)
    return db_user