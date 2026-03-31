#errors.py
from domain.platform import VideoPlatform

class DomainError(Exception):
    """Base class for domain-level errors."""
    
    def __init__(self, message: str, error_code: str | None = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.replace("Error", "").upper()
        super().__init__(message)

# ============================================================================
# AUTHENTICATION ERRORS
# ============================================================================

class AuthenticationError(DomainError):
    """Base class for authentication-related errors."""

class NotAuthenticatedError(AuthenticationError):
    def __init__(self):
        super().__init__(
            message="Not authenticated",
            error_code="NOT_AUTHENTICATED"
        )

class InvalidCredentialsError(AuthenticationError):
    def __init__(self):
        super().__init__(
            message="Invalid authentication credentials",
            error_code="INVALID_CREDENTIALS"
        )

class UserNotFoundError(AuthenticationError):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(
            message="User not found",
            error_code="USER_NOT_FOUND"
        )

class PasswordChangeRequiredError(AuthenticationError):
    def __init__(self):
        super().__init__(
            message="Password change required",
            error_code="PASSWORD_CHANGE_REQUIRED"
        )

class PasswordAlreadyChangedError(AuthenticationError):
    def __init__(self):
        super().__init__(
            message="Initial password has already been changed. "
                   "Password cannot be changed again through this endpoint.",
            error_code="PASSWORD_ALREADY_CHANGED"
        )

# ============================================================================
# AGENT ERRORS
# ============================================================================

class AgentError(DomainError):
    """Base class for agent-related errors."""

class AgentAlreadyExistsError(AgentError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(
            message=f"Agent with name '{name}' already exists",
            error_code="AGENT_ALREADY_EXISTS"
        )

class AgentNotFoundError(AgentError):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        super().__init__(
            message=f"Agent with ID '{agent_id}' not found",
            error_code="AGENT_NOT_FOUND"
        )

class AgentIsAuditingError(AgentError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            message=f"Cannot modify agent '{agent_name}' while it is running an audit session.",
            error_code="AGENT_IS_AUDITING"
        )

# ============================================================================
# SESSION ERRORS
# ============================================================================

class SessionError(DomainError):
    """Base class for session-related errors."""

class AgentAlreadyAuditingError(SessionError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            message=f"Agent '{agent_name}' is already auditing",
            error_code="AGENT_ALREADY_AUDITING"
        )

class AgentNotAuditingError(SessionError):
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        super().__init__(
            message=f"Agent '{agent_name}' is not currently auditing",
            error_code="AGENT_NOT_AUDITING"
        )

class SessionNotFoundError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            message=f"Session with ID '{session_id}' not found",
            error_code="SESSION_NOT_FOUND"
        )

class SessionAlreadyCompletedError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            message=f"Session '{session_id}' is already completed",
            error_code="SESSION_ALREADY_COMPLETED"
        )

class SessionNotRunningError(SessionError):
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__(
            message=f"Session '{session_id}' is not currently running",
            error_code="SESSION_NOT_RUNNING"
        )

# ============================================================================
# PLATFORM ERRORS
# ============================================================================

class PlatformError(DomainError):
    """Base class for platform-related errors."""

class UnsupportedPlatformError(PlatformError):
    def __init__(self, platform: str, supported: list[str]):
        self.platform = platform
        self.supported = supported
        super().__init__(
            message=f"Unsupported platform '{platform}'. "
                   f"Supported platforms: {', '.join(supported)}",
            error_code="UNSUPPORTED_PLATFORM"
        )

# ============================================================================
# VIDEO ERRORS
# ============================================================================

class VideoError(DomainError):
    """Base class for video-related errors."""

class VideoNotFoundError(VideoError):
    def __init__(self, platform: VideoPlatform):
        self.platform = platform
        super().__init__(
            message=f"Video with provided video_id does not exist on platform '{platform.value}'.",
            error_code="VIDEO_NOT_FOUND"
        )

class VideoDownloadError(VideoError):
    def __init__(self, platform: str, video_id: str, reason: str):
        self.platform = platform
        self.video_id = video_id
        self.reason = reason
        super().__init__(
            message=f"Failed to download video from {platform} (ID: {video_id}): {reason}",
            error_code="VIDEO_DOWNLOAD_FAILED"
        )

# ============================================================================
# VIDEO LOG ERRORS
# ============================================================================

class VideoLogError(DomainError):
    """Base class for video log-related errors."""

class NoVideoLogsFoundError(VideoLogError):
    def __init__(self, context: str):
        self.context = context
        super().__init__(
            message=f"No video logs found for {context}",
            error_code="NO_VIDEO_LOGS_FOUND"
        )

# ============================================================================
# PREDICTOR ERRORS
# ============================================================================

class PredictorError(DomainError):
    """Base class for predictor-related errors."""

class UnsupportedPredictorVersionError(PredictorError):
    def __init__(self, version: str, supported_versions: list[str]):
        self.version = version
        self.supported_versions = supported_versions
        super().__init__(
            message=f"Unsupported predictor version '{version}'. "
                   f"Supported versions: {', '.join(supported_versions)}",
            error_code="UNSUPPORTED_PREDICTOR_VERSION"
        )

# ============================================================================
# VALIDATION ERRORS
# ============================================================================

class ValidationError(DomainError):
    """Base class for validation-related errors."""

class InvalidUserProfileSchemaError(ValidationError):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(
            message=f"Invalid user profile schema: {reason}",
            error_code="INVALID_USER_PROFILE_SCHEMA"
        )