from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import decode_access_token
from domain.models.user import User
from domain.errors import AlreadyAuthenticatedError

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

async def get_current_user_if_password_changed(
    current_user: User = Depends(get_current_user),
) -> User:
    
    if current_user.must_change_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password change required",
        )
    
    return current_user

async def ensure_not_authenticated(request: Request) -> None:
    token = request.cookies.get("access_token")
    
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            
            if user_id:
                raise AlreadyAuthenticatedError()
        except HTTPException:
            pass