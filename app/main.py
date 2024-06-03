from fastapi import FastAPI
from .routers import users, contacts
from .database import SessionLocal, engine, get_db
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
