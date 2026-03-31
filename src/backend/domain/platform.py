from enum import Enum

class VideoPlatform(str, Enum):
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    YOUTUBE = "YouTube"

class PlatformRegistry:    
    @classmethod
    def get_supported_platforms(cls) -> list[str]:
        return [platform.value for platform in VideoPlatform]
    
    @classmethod
    def is_valid_platform(cls, platform: str) -> bool:
        return platform in cls.get_supported_platforms()
    
    @classmethod
    def validate_platform(cls, platform: str) -> VideoPlatform:
        if not cls.is_valid_platform(platform):
            from domain.errors import UnsupportedPlatformError
            raise UnsupportedPlatformError(
                platform=platform,
                supported=cls.get_supported_platforms()
            )
        return VideoPlatform(platform)