from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from exeptions.base import AppException
from exeptions.infrastructure import DatabaseException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    content = exc.to_dict()
    if exc.original_error:
        content["detail"]["original_error"] = str(exc.original_error)
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Ошибка валидации данных",
            "status_code": 422,
            "detail": {"validation_errors": errors}
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "Внутренняя ошибка сервера",
            "status_code": 500
        }
    )