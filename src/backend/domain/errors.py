from domain.video import VideoPlatform

class DomainError(Exception):
    """Base class for domain-level errors."""

class UnsupportedPlatformError(DomainError):
    def __init__(self, platform: str, supported: list[str]):
        self.platform = platform
        self.supported = supported
        super().__init__(
            f"Invalid platform '{platform}'. "
            f"Supported platforms: {', '.join(supported)}"
        )


class VideoNotFoundError(DomainError):
    def __init__(self, platform: VideoPlatform):
        self.platform = platform
        super().__init__(
            f"Video does not exist on platform '{platform.value}'."
        )