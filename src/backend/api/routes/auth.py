from fastapi import APIRouter, Depends, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.settings import settings
from core.database import get_db
from api.deps import (
    get_current_user,
    get_current_user_if_password_changed,
    ensure_not_authenticated,
)
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
)
from services.auth_service import AuthService
from domain.models.user import User

router = APIRouter()

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: Request,
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(ensure_not_authenticated),
):
    
    user, access_token = await AuthService.authenticate_user(
        db=db,
        password=payload.password,
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return LoginResponse(
        message="Login successful",
        must_change_password=user.must_change_password,
    )

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
):
    
    await AuthService.change_password(
        db=db,
        user=current_user,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
    )
    
    from core.security import create_access_token
    from datetime import timedelta
    from core.settings import settings
    
    new_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    
    return ChangePasswordResponse(
        message="Password changed successfully"
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    response: Response,
    #current_user: User = Depends(get_current_user_if_password_changed),
):
    response.delete_cookie(key="access_token")
    
    return {"message": "Logged out successfully"}

@router.get(
    "/verify",
    status_code=status.HTTP_200_OK,
)
async def verify_auth(
    current_user: User = Depends(get_current_user),
):
    if current_user.must_change_password:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password change required"
        )
    
    return {
        "authenticated": True,
        "must_change_password": False
    }