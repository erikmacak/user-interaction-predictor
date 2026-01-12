from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from domain.errors import DomainError

def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request body",
            "details": exc.errors(),
        },
    )

def domain_exception_handler(_: Request, exc: DomainError):
    return JSONResponse(
        status_code=404,
        content={
            "error": str(exc),
        },
    )