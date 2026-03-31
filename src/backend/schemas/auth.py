from pydantic import BaseModel, ConfigDict, Field

class LoginRequest(BaseModel):
    password: str = Field(..., min_length=1)
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class LoginResponse(BaseModel):
    message: str
    must_change_password: bool
    
    model_config = ConfigDict(frozen=True)

class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=12)
    confirm_password: str = Field(..., min_length=12)
    
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

class ChangePasswordResponse(BaseModel):
    message: str
    
    model_config = ConfigDict(frozen=True)