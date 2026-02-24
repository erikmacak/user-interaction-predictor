from typing import Dict
from domain.video import VideoPlatform, VideoSource
from services.video_availability.base import BaseVideoAvailabilityService
from services.video_availability.tiktok import TikTokAvailabilityService
from services.video_availability.youtube import YouTubeAvailabilityService
from services.video_availability.instagram import InstagramAvailabilityService
from domain.errors import VideoAvailabilityNotImplementedError

class VideoAvailabilityRegistry:
    _services: Dict[VideoPlatform, BaseVideoAvailabilityService] = {
        VideoPlatform.TIKTOK: TikTokAvailabilityService(),
        VideoPlatform.YOUTUBE: YouTubeAvailabilityService(),
        VideoPlatform.INSTAGRAM: InstagramAvailabilityService(),
    }
    
    @classmethod
    def exists(cls, video: VideoSource) -> bool:
        try:
            service = cls._services[video.platform]
        except KeyError:
            raise VideoAvailabilityNotImplementedError(video.platform)
        
        return service.exists(video)