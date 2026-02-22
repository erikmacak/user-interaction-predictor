from pydantic import BaseModel, Field
from core.settings import settings

class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1)

class LoginResponse(BaseModel):
    message: str
    must_change_password: bool

class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH)
    confirm_password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH)

class ChangePasswordResponse(BaseModel):
    message: str