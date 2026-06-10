import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.api.error_handlers import error_payload
from backend.core.config import settings
from backend.middleware.rate_limit import check_rate_limit


def register_trace_and_rate_limit_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def trace_and_rate_limit(request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        try:
            allowed, remaining = await check_rate_limit(request)
            rate_headers = {
                "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                "X-RateLimit-Remaining": str(remaining),
            }
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content=error_payload(429, "rate_limit_exceeded", "Too Many Requests", trace_id),
                    headers={**rate_headers, "x-trace-id": trace_id, "Retry-After": "60"},
                )
            response = await call_next(request)
            response.headers["x-trace-id"] = trace_id
            response.headers.update(rate_headers)
            return response
        except Exception:
            return JSONResponse(
                status_code=500,
                content=error_payload(500, "internal_server_error", "Internal Server Error", trace_id),
                headers={"x-trace-id": trace_id},
            )
