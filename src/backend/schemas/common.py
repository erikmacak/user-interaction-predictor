from typing import Optional, Any, List, Dict
from pydantic import BaseModel

class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str
    type: Optional[str] = None

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: str

class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None