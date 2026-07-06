from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from .config import URL

class Base(DeclarativeBase):
    pass


engine = create_engine(URL) #engine just connection to db server


def create_table():
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


