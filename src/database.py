from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from dotenv import dotenv_values
from .config import user, pin, host, port, db_name

class Base(DeclarativeBase):
    pass


db_url = f"postgresql+psycopg2://{user}:{pin}@{host}:{port}/{db_name}"
engine = create_engine(db_url) #engine just connection to db server


def create_table():
    Base.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


