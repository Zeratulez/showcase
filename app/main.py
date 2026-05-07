from fastapi import FastAPI

from app.api.endpoints import auth, items, users
from app.core.logging import setup_logging
from app.middleware import logging_middleware, redis_middleware

setup_logging(is_production=False)

app = FastAPI()

app.add_middleware(logging_middleware.LoggingMiddleware)
app.middleware("http")(redis_middleware.rate_limit_middleware)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(users.router)