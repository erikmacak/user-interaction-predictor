import requests

from domain.video import VideoSource
from services.video_availability.base import BaseVideoAvailabilityService
from services.http_client import HttpClient

class YouTubeAvailabilityService(BaseVideoAvailabilityService):
    OEMBED_URL = "https://www.youtube.com/oembed"

    def exists(self, video: VideoSource) -> bool:
        params = {
            "url": f"https://www.youtube.com/watch?v={video.video_id}",
        }

        try:
            response = HttpClient.get(
                self.OEMBED_URL,
                params=params,
            )
        except requests.RequestException:
            return False

        if response.status_code != 200:
            return False

        data = response.json()

        return (
            "html" in data
            and data.get("provider_name") == "YouTube"
        )