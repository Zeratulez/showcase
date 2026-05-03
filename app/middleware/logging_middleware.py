import time
import uuid
import structlog

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        clear_contextvars()
        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()
        bind_contextvars(request_id=request_id)
        log = logger.bind(
            method=request.method,
            path=request.url.path,
        )
        await log.ainfo("request_started")
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_method = log.awarning if duration_ms > 1000 else log.ainfo
            await log_method(
                "request_finished",
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            return response
        except Exception as _:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            await log.aerror(
                "request_failed",
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise