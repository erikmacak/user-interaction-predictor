from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime, timezone

from domain.errors import (
    DomainError,
    UnsupportedPredictorVersionError,
    AlreadyAuthenticatedError,
    PasswordAlreadyChangedError,
)

def _get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()

def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "details": errors,
            "timestamp": _get_timestamp(),
        },
    )

def domain_exception_handler(_: Request, exc: DomainError):
    status_code = 404
    error_code = "RESOURCE_NOT_FOUND"

    if isinstance(exc, UnsupportedPredictorVersionError):
        status_code = 400
        error_code = "UNSUPPORTED_VERSION"
    elif isinstance(exc, AlreadyAuthenticatedError):
        status_code = 409
        error_code = "ALREADY_AUTHENTICATED"
    elif isinstance(exc, PasswordAlreadyChangedError):
        status_code = 403
        error_code = "PASSWORD_ALREADY_CHANGED"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": str(exc),
            "error_code": error_code,
            "timestamp": _get_timestamp(),
        },
    )