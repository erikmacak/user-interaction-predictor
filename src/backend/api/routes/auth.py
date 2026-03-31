from datetime import timedelta

from fastapi import APIRouter, Depends, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from core.database import get_db
from core.security import create_access_token
from core.settings import settings
from domain.models.user import User
from domain.errors import InvalidCredentialsError, PasswordChangeRequiredError
from schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LoginResponse,
)
from services.auth_service import AuthService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    try:
        user, access_token = await AuthService.authenticate_user(
            db=db,
            password=payload.password,
        )
        
        _set_auth_cookie(response, access_token)
        
        return LoginResponse(
            message="Login successful",
            must_change_password=user.must_change_password,
        )
    
    except InvalidCredentialsError:
        _clear_auth_cookie(response)
        raise

@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChangePasswordResponse:
    await AuthService.change_password(
        db=db,
        user=current_user,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
    )
    
    new_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    _set_auth_cookie(response, new_token)
    
    return ChangePasswordResponse(
        message="Password changed successfully"
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(response: Response) -> dict[str, str]:
    _clear_auth_cookie(response)
    return {"message": "Logged out successfully"}

@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
)
async def verify_auth(
    current_user: User = Depends(get_current_user),
) -> dict[str, bool]:
    if current_user.must_change_password:
        raise PasswordChangeRequiredError()
    
    return {
        "authenticated": True,
        "must_change_password": False
    }

def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

def _clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(key="access_token")