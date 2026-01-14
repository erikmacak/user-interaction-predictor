from pydantic import BaseModel, ConfigDict
from core.version import get_app_version

class AppSettings(BaseModel):
    APP_NAME: str = "User Interaction Predictor API"
    APP_VERSION: str = get_app_version()

    PREDICTOR_VERSION: str = "v1"

    allow_instagram_without_availability_check: bool = False

    model_config = ConfigDict(
        frozen=True
    )

settings = AppSettings()