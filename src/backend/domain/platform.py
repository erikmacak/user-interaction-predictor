from enum import Enum
from typing import List

class VideoPlatform(str, Enum):
    YOUTUBE = "YouTube"
    TIKTOK = "TikTok"
    INSTAGRAM = "Instagram"

class PlatformRegistry:
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        return [platform.value for platform in VideoPlatform]
    
    @classmethod
    def is_valid_platform(cls, platform: str) -> bool:
        return platform in cls.get_supported_platforms()
    
    @classmethod
    def validate_platform(cls, platform: str) -> str:
        if not cls.is_valid_platform(platform):
            from domain.errors import UnsupportedPlatformError
            raise UnsupportedPlatformError(
                platform=platform,
                supported=cls.get_supported_platforms()
            )
        return platform