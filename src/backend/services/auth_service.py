from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from domain.models.user import User
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    PasswordPolicy,
)
from core.settings import settings
from domain.errors import PasswordAlreadyChangedError

class AuthService:
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        password: str,
    ) -> tuple[User, str]:
        
        result = await db.execute(
            select(User).where(User.username == "admin")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        return user, access_token
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        new_password: str,
        confirm_password: str,
    ) -> None:
        
        if user.password_changed_at is not None:
            raise PasswordAlreadyChangedError()
        
        if new_password != confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
            )
        
        is_valid, error_message = PasswordPolicy.validate(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message,
            )
        
        password_hash = get_password_hash(new_password)

        user.password_hash = password_hash
        user.must_change_password = False
        user.password_changed_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)