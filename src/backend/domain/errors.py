from domain.video import VideoPlatform

class DomainError(Exception):
    """Base class for domain-level errors."""

class InvalidUserProfileSchemaError(DomainError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            f"Invalid user profile schema: {reason}"
        )

class UnsupportedPlatformError(DomainError):
    def __init__(self, platform: str, supported: list[str]):
        self.platform = platform
        self.supported = supported
        super().__init__(
            f"Unsupported platform '{platform}'. "
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

class VideoDownloadError(DomainError):
    def __init__(self, platform: str, video_id: str, reason: str):
        self.platform = platform
        self.video_id = video_id
        self.reason = reason
        super().__init__(
            f"Failed to download video from {platform} (ID: {video_id}): {reason}"
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

class AgentError(DomainError):
    """Base class for agent-related errors."""

class AgentAlreadyExistsError(AgentError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(
            f"Agent with name '{name}' already exists"
        )

class AgentNotFoundError(AgentError):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        super().__init__(
            f"Agent with ID '{agent_id}' not found"
        )

class AgentIsAuditingError(AgentError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            f"Cannot modify agent '{agent_name}' while it is running an audit session."
        )

class SessionError(DomainError):
    """Base class for session-related errors."""

class AgentAlreadyAuditingError(SessionError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            f"Agent '{agent_name}' is already auditing",
            "AGENT_ALREADY_AUDITING"
        )

class AgentNotAuditingError(SessionError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            f"Agent '{agent_name}' is not currently auditing",
            "AGENT_NOT_AUDITING"
        )

class SessionNotFoundError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            f"Session with ID '{session_id}' not found",
            "SESSION_NOT_FOUND"
        )

class SessionAlreadyCompletedError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            f"Session '{session_id}' is already completed",
            "SESSION_ALREADY_COMPLETED"
        )

class SessionNotRunningError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            f"Session '{session_id}' is not currently running"
        )