from domain.video import VideoSource
from services.video_availability.base import BaseVideoAvailabilityService

class TikTokAvailabilityService(BaseVideoAvailabilityService):
    def exists(self, video: VideoSource) -> bool:
        return False