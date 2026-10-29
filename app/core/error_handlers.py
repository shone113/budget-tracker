import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def error_response(status_code: int, message: str, details: list | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"message": message, "details": details or []})


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return error_response(exc.status_code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        details = [{"field": err["loc"][-1], "message": err["msg"]} for err in exc.errors()]
        return error_response(422, "Invalid input.", details)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        return error_response(500, "Internal server error.")