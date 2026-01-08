from typing import Dict

from domain.video import VideoPlatform, VideoSource
from services.video_availability.base import BaseVideoAvailabilityService
from services.video_availability.instagram import InstagramAvailabilityService
from services.video_availability.tiktok import TikTokAvailabilityService
from services.video_availability.youtube import YouTubeAvailabilityService

class VideoAvailabilityRegistry:
    _services: Dict[VideoPlatform, BaseVideoAvailabilityService] = {
        #VideoPlatform.INSTAGRAM: InstagramAvailabilityService(),
        VideoPlatform.TIKTOK: TikTokAvailabilityService(),
        VideoPlatform.YOUTUBE: YouTubeAvailabilityService(),
    }

    @classmethod
    def exists(cls, video: VideoSource) -> bool:
        try:
            service = cls._services[video.platform]
        except KeyError:
            raise ValueError(
                f"Video availability check not implemented for {video.platform}"
            )

        return service.exists(video)