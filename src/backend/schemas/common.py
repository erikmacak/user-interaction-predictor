from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

class ErrorDetail(BaseModel):
    field: str | None = None
    message: str
    type: str | None = None
    
    model_config = ConfigDict(frozen=True)

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: list[ErrorDetail] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(frozen=True)

class SuccessResponse(BaseModel):
    message: str
    data: dict[str, Any] | None = None
    
    model_config = ConfigDict(frozen=True)