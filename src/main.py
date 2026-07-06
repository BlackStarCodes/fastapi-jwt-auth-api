from fastapi import FastAPI
from .routers import auth, users
from .database import create_table

create_table()


app = FastAPI()


app.include_router(auth.router)
app.include_router(users.router)