from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from core.version import get_app_version

class AppSettings(BaseSettings):
    APP_NAME: str = "User Interaction Predictor API"
    APP_VERSION: str = get_app_version()
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    INITIAL_ADMIN_PASSWORD: str
    
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    
    PREDICTOR_VERSION: str = "v1"
    allow_instagram_without_availability_check: bool = False
    
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_DIGIT: bool = True
    REQUIRE_SPECIAL_CHAR: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=True,
    )

settings = AppSettings()