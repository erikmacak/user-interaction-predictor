from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from domain.errors import DomainError, UnsupportedPredictorVersionError

def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid request body",
            "details": exc.errors(),
        },
    )

def domain_exception_handler(_: Request, exc: DomainError):
    status_code = 404

    if isinstance(exc, UnsupportedPredictorVersionError):
        status_code = 400

    return JSONResponse(
        status_code=status_code,
        content={
            "error": str(exc),
        },
    )