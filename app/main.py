from fastapi import FastAPI

from app.api.endpoints import auth, items, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(users.router)