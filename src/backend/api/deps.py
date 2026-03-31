from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from core.security import decode_access_token
from domain.models.user import User
from domain.errors import (
    NotAuthenticatedError,
    InvalidCredentialsError,
    UserNotFoundError,
    PasswordChangeRequiredError,
)

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    
    if not token:
        raise NotAuthenticatedError()
    
    user_id = _decode_token(token)
    user = await _get_user_by_id(db, user_id)
    
    if user is None:
        raise UserNotFoundError(user_id=str(user_id))
    
    return user

async def get_current_user_if_password_changed(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.must_change_password:
        raise PasswordChangeRequiredError()
    
    return current_user

def _decode_token(token: str) -> UUID:
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise InvalidCredentialsError()
        
        return UUID(user_id)
    except Exception:
        raise InvalidCredentialsError()

async def _get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()