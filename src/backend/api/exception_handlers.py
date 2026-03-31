from datetime import datetime, timezone
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from domain.errors import (
    DomainError,
    NotAuthenticatedError,
    InvalidCredentialsError,
    UserNotFoundError,
    PasswordChangeRequiredError,
    PasswordAlreadyChangedError,
    AgentNotFoundError,
    AgentAlreadyExistsError,
    AgentIsAuditingError,
    SessionNotFoundError,
    SessionAlreadyCompletedError,
    SessionNotRunningError,
    AgentAlreadyAuditingError,
    AgentNotAuditingError,
    UnsupportedPlatformError,
    VideoNotFoundError,
    UnsupportedPredictorVersionError,
    InvalidUserProfileSchemaError,
    NoVideoLogsFoundError,
)

HTTP_STATUS_MAP = {
    NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    PasswordChangeRequiredError: status.HTTP_403_FORBIDDEN,
    PasswordAlreadyChangedError: status.HTTP_409_CONFLICT,
    AgentNotFoundError: status.HTTP_404_NOT_FOUND,
    AgentAlreadyExistsError: status.HTTP_409_CONFLICT,
    AgentIsAuditingError: status.HTTP_409_CONFLICT,
    SessionNotFoundError: status.HTTP_404_NOT_FOUND,
    SessionAlreadyCompletedError: status.HTTP_409_CONFLICT,
    SessionNotRunningError: status.HTTP_409_CONFLICT,
    AgentAlreadyAuditingError: status.HTTP_409_CONFLICT,
    AgentNotAuditingError: status.HTTP_409_CONFLICT,
    UnsupportedPlatformError: status.HTTP_400_BAD_REQUEST,
    VideoNotFoundError: status.HTTP_404_NOT_FOUND,
    UnsupportedPredictorVersionError: status.HTTP_400_BAD_REQUEST,
    InvalidUserProfileSchemaError: status.HTTP_400_BAD_REQUEST,
    NoVideoLogsFoundError: status.HTTP_404_NOT_FOUND,
}

def _get_status_code_for_error(error: DomainError) -> int:
    return HTTP_STATUS_MAP.get(type(error), status.HTTP_500_INTERNAL_SERVER_ERROR)

def _build_error_response(
    error_code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": message,
            "error_code": error_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = _get_status_code_for_error(exc)
    return _build_error_response(exc.error_code, exc.message, status_code)

async def validation_error_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    errors = exc.errors()
    
    if errors:
        first_error = errors[0]
        field_parts = [str(loc) for loc in first_error["loc"] if loc != "body"]
        field = field_parts[-1] if field_parts else "unknown"
        error_type = first_error["type"]
        error_msg = first_error["msg"]
        
        message = _format_user_friendly_error(field, error_type, error_msg, first_error)
    else:
        message = "Validation failed"
    
    return _build_error_response(
        error_code="VALIDATION_ERROR",
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )

def _format_user_friendly_error(
    field: str,
    error_type: str,
    error_msg: str,
    error_details: dict
) -> str:
    field_name_map = {
        'state_file_data': 'User profile data',
        'name': 'Agent name',
        'platform': 'Platform',
        'predictor_version': 'Predictor version',
        'new_password': 'New password',
        'confirm_password': 'Password confirmation',
    }
    
    friendly_field = field_name_map.get(field, field.replace('_', ' ').title())
    
    if error_type == "string_too_long":
        max_length = error_details.get("ctx", {}).get("max_length", "unknown")
        return f"{friendly_field} is too long. Maximum length is {max_length} characters."
    
    elif error_type == "string_too_short":
        min_length = error_details.get("ctx", {}).get("min_length", "unknown")
        return f"{friendly_field} is too short. Minimum length is {min_length} characters."
    
    elif error_type == "value_error":
        if "Invalid user profile schema" in error_msg:
            schema_error = error_msg.replace("Value error, ", "")
            schema_error = schema_error.replace("Invalid user profile schema: ", "")
            
            if "Missing required field" in schema_error:
                missing_field = schema_error.split("'")[1] if "'" in schema_error else "unknown"
                readable_field = missing_field.replace('user_profile.', '').replace('_', ' ').title()
                return f"User profile is missing required field: {readable_field}"
            
            return f"User profile validation failed: {schema_error}"
        
        return error_msg.replace("Value error, ", "")
    
    elif error_type == "missing":
        return f"{friendly_field} is required"
    
    elif error_type == "json_invalid":
        return f"{friendly_field} must be valid JSON format"
    
    elif error_type == "string_pattern_mismatch":
        return f"{friendly_field} format is invalid"
    
    else:
        return f"{friendly_field}: {error_msg}"

async def pydantic_validation_error_handler(
    request: Request,
    exc: ValidationError
) -> JSONResponse:
    errors = exc.errors()
    
    if errors:
        first_error = errors[0]
        field = " -> ".join(str(loc) for loc in first_error["loc"])
        error_msg = first_error["msg"]
        message = f"Field '{field}': {error_msg}"
    else:
        message = "Validation failed"
    
    return _build_error_response(
        error_code="VALIDATION_ERROR",
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )