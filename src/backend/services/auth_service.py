from datetime import datetime, timedelta, timezone

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
    ADMIN_USERNAME = "admin"
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        password: str,
    ) -> tuple[User, str]:
        user = await AuthService._get_admin_user(db)
        
        AuthService._validate_credentials(password, user)
        
        access_token = AuthService._create_token(user)
        
        return user, access_token
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        new_password: str,
        confirm_password: str,
    ) -> None:
        AuthService._validate_password_change(user, new_password, confirm_password)
        
        AuthService._update_user_password(user, new_password)
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    @staticmethod
    async def _get_admin_user(db: AsyncSession) -> User:
        result = await db.execute(
            select(User).where(User.username == AuthService.ADMIN_USERNAME)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        
        return user
    
    @staticmethod
    def _validate_credentials(password: str, user: User) -> None:
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
    
    @staticmethod
    def _create_token(user: User) -> str:
        return create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
    
    @staticmethod
    def _validate_password_change(
        user: User,
        new_password: str,
        confirm_password: str
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
    
    @staticmethod
    def _update_user_password(user: User, new_password: str) -> None:
        password_hash = get_password_hash(new_password)
        
        user.password_hash = password_hash
        user.must_change_password = False
        user.password_changed_at = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)