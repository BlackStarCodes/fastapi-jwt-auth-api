from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, select
from typing import Optional
from .database import Base


class UserORM(Base):
    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    fullname: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))