import re
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.settings import settings
from domain.errors import InvalidCredentialsError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class PasswordPolicy:
    MIN_LENGTH = 12
    
    SPECIAL_CHARS = r"[!@#$%^&*(),.?\":{}|<>]"
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        errors = PasswordPolicy._collect_validation_errors(password)
        
        if errors:
            error_message = "Password validation failed: " + "; ".join(errors)
            return False, error_message
        
        return True, ""
    
    @staticmethod
    def _collect_validation_errors(password: str) -> list[str]:
        errors = []
        
        if len(password) < PasswordPolicy.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordPolicy.MIN_LENGTH} characters long")
        
        if settings.REQUIRE_UPPERCASE and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if settings.REQUIRE_LOWERCASE and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if settings.REQUIRE_DIGIT and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if settings.REQUIRE_SPECIAL_CHAR and not re.search(PasswordPolicy.SPECIAL_CHARS, password):
            errors.append(
                f"Password must contain at least one special character "
                f"(!@#$%^&*(),.?\":{{}}|<>)"
            )
        
        return errors


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = _calculate_expiration(expires_delta)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise InvalidCredentialsError()

def _calculate_expiration(expires_delta: timedelta | None) -> datetime:
    if expires_delta:
        return datetime.now(timezone.utc) + expires_delta
    return datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)