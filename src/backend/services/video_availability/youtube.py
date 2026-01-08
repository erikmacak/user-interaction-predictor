from domain.video import VideoSource
from services.video_availability.base import BaseVideoAvailabilityService

class YouTubeAvailabilityService(BaseVideoAvailabilityService):
    def exists(self, video: VideoSource) -> bool:
        return False