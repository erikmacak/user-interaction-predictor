from domain.video import VideoSource
from domain.errors import VideoAvailabilityNotImplementedError
from services.video_availability.base import BaseVideoAvailabilityService

class InstagramAvailabilityService(BaseVideoAvailabilityService):
    def exists(self, video: VideoSource) -> bool:
        raise VideoAvailabilityNotImplementedError(video.platform)

# NOTE:
# Instagram currently requires authentication for its oEmbed endpoint.
# Due to this limitation, the video existence verification mechanism is intentionally not implemented for the Instagram platform yet.