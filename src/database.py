from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from dotenv import dotenv_values
from .config import url

class Base(DeclarativeBase):
    pass


engine = create_engine(url) #engine just connection to db server


def create_table():
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


