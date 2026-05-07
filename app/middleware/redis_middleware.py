import time

from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core import redis_client
from app.core.config import settings


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_window = int(time.time() // settings.REDIS_RATE_LIMIT_WINDOW)
    redis_key = f"rate_limit:{client_ip}:{current_window}"
    current_count = await redis_client.redis_client.incr(redis_key)
    if current_count == 1:
        await redis_client.redis_client.expire(redis_key, settings.REDIS_RATE_LIMIT_WINDOW)
    if current_count > settings.REDIS_RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later"},
            headers={
                "X-RateLimit-Limit": str(settings.REDIS_RATE_LIMIT_REQUESTS),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(settings.REDIS_RATE_LIMIT_WINDOW),
            }
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(settings.REDIS_RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(settings.REDIS_RATE_LIMIT_REQUESTS - current_count)
    return response