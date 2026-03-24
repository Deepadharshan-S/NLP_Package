from fastapi import FastAPI
from app.api.routes import auth
from app.db.init_db import init_db

app = FastAPI()

init_db()
app.include_router(auth.router)