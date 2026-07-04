from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional, Annotated
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, Session
from dotenv import dotenv_values
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone


class Base(DeclarativeBase):
    pass 


class UserORM(Base):
    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String(50), unique=True)
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


SECRET_KEY= v["SECRET_KEY"]
ALGO = v["ALGORITHM"]
TOKEN_EXPIRE_MINS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


app = FastAPI()


class UserCreate(BaseModel):
    name: str
    fullname: str | None = None
    email: str
    

class UserSignup(UserCreate):
    password: str
#plain password gonna be username + first 2 letter of email. changing user info may cause problem since you can deduce plain password anymore


class UserOut(UserCreate):
    id : int
    model_config = { "from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type:str


class TokenData(BaseModel):
    username: str | None = None


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


@app.post("/users/", response_model= UserOut)
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


@app.post("/login/")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: session_dependency) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password!", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=TOKEN_EXPIRE_MINS)
    access_token = create_access_token(data={"sub":user.name}, expires_delta= access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@app.post("/login_verify/")
async def login_verify(username: str, password: str, session: session_dependency):
    user = session.scalar(select(UserORM).where(UserORM.name == username))
    if not user:
        verify_pass(password, dummy)
        raise HTTPException(status_code=401, detail="wrong credentials!")
    
    if not verify_pass(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="wrong credentials!")
    return {"message": "signed in"}



@app.get("/users/", response_model=List[UserOut])
async def read_users(
    session: session_dependency, 
    offset: int = 0, #just synonyms for start
    limit: Annotated[int, Query(le=100)] = 100,):
    users = session.scalars(select(UserORM).offset(offset).limit(limit)).all()
    return users


@app.get("/users/me", response_model=UserOut)
async def read_current_user(user:Annotated[UserCreate, Depends(get_current_user)]):
    return user


@app.get("/users/{user_id}", response_model=UserOut)
async def read_a_user(
    user_id: int,
    session: session_dependency,):
    user = session.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user


@app.delete("/users/{user_id}")
async def remove_user(
    user_id: int,
    session: session_dependency
) :
    user = session.get(UserORM, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"status":f"successfully removed the user with user id:{user_id} !"}


@app.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user: UserSignup,
    user_id: int,
    session: session_dependency
) :
    db_user = session.get(UserORM, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    existing = session.scalar(select(UserORM).where(UserORM.name == user.name))
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail="username already taken, enter new username!")
    
    existing = session.scalar((select(UserORM).where(UserORM.email == user.email)))
    if existing and existing.id != user_id:
        raise HTTPException(status_code=409, detail="email already in use!, enter new email")
    
    db_user.name = user.name
    db_user.fullname = user.fullname
    db_user.email = user.email
    db_user.hashed_password = pwd_hashed(user.password)

    session.commit()
    session.refresh(db_user)
    return db_user