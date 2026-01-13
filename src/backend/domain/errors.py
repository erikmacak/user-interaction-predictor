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

class UnsupportedPredictorVersionError(DomainError):
    def __init__(self, version: str, supported_versions: list[str]):
        self.version = version
        self.supported_versions = supported_versions
        super().__init__(
            f"Unsupported predictor version '{version}'. "
            f"Supported versions: {', '.join(supported_versions)}"
        )