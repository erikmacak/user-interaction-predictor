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
            f"Video with provided video_id does not exist on platform '{platform.value}'."
        )

class VideoAvailabilityNotImplementedError(DomainError):
    def __init__(self, platform: VideoPlatform):
        self.platform = platform
        super().__init__(
            f"Video availability check not implemented for {platform.value}"
        )

class UnsupportedPredictorVersionError(DomainError):
    def __init__(self, version: str, supported_versions: list[str]):
        self.version = version
        self.supported_versions = supported_versions
        super().__init__(
            f"Unsupported predictor version '{version}'. "
            f"Supported versions: {', '.join(supported_versions)}"
        )

class AuthenticationError(DomainError):
    """Base class for authentication-related errors."""

class AlreadyAuthenticatedError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "User is already authenticated. Please logout first to login again."
        )

class PasswordAlreadyChangedError(AuthenticationError):
    def __init__(self):
        super().__init__(
            "Initial password has already been changed. "
            "Password cannot be changed again through this endpoint."
        )