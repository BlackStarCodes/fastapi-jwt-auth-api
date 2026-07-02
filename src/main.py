from fastapi import FastAPI, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Annotated
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase, Session

class Base(DeclarativeBase):
    pass 

class User(Base):
    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String(50))

user = 'postgres'
pin = 'We rock'
host = '127.0.0.1'
port = 5432
db_name = 'proj2_auth'


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


@app.post("/users/")
async def new_user(user: UserCreate, session: session_dependency):
    user = User(
        name = user.name,
        fullname = user.fullname,
        email = user.email
    )
    session.add(user)
    session.commit()
    return user


@app.get("/users/")
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