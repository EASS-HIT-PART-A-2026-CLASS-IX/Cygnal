from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_payload(status_code: int, error: str, detail, trace_id: str) -> dict:
    return {"status": status_code, "error": error, "detail": detail, "trace_id": trace_id}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        error_names = {401: "unauthorized", 403: "forbidden", 404: "resource_not_found"}
        return JSONResponse(
            status_code=exc.status_code,
            content=error_payload(
                exc.status_code,
                error_names.get(exc.status_code, "http_error"),
                exc.detail,
                request.state.trace_id,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=error_payload(422, "validation_error", jsonable_encoder(exc.errors()), request.state.trace_id),
        )
