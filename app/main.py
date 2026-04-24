from fastapi import FastAPI

from app.api.endpoints import auth, items

app = FastAPI()

app.include_router(auth.router)
app.include_router(items.router)