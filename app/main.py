from fastapi import FastAPI

from app.api.endpoints import auth, items, users
from app.middleware import redis_middleware

app = FastAPI()

app.middleware("http")(redis_middleware.rate_limit_middleware)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(users.router)