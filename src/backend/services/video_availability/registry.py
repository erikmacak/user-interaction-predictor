from typing import Dict

from core.settings import settings
from domain.video import VideoPlatform, VideoSource
from services.video_availability.base import BaseVideoAvailabilityService
from services.video_availability.instagram import InstagramAvailabilityService
from services.video_availability.tiktok import TikTokAvailabilityService
from services.video_availability.youtube import YouTubeAvailabilityService
from domain.errors import VideoAvailabilityNotImplementedError

class VideoAvailabilityRegistry:
    _services: Dict[VideoPlatform, BaseVideoAvailabilityService] = {
        VideoPlatform.TIKTOK: TikTokAvailabilityService(),
        VideoPlatform.YOUTUBE: YouTubeAvailabilityService(),
    }

    @classmethod
    def exists(cls, video: VideoSource) -> bool:
        if (
            video.platform == VideoPlatform.INSTAGRAM
            and settings.allow_instagram_without_availability_check
        ):
            return True

        try:
            service = cls._services[video.platform]
        except KeyError:
            raise VideoAvailabilityNotImplementedError(video.platform)

        return service.exists(video)