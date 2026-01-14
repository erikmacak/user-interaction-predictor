from dataclasses import dataclass
from enum import Enum

class VideoPlatform(str, Enum):
    INSTAGRAM = "Instagram"
    TIKTOK = "TikTok"
    YOUTUBE = "YouTube"

@dataclass(frozen=True)
class VideoSource:
    platform: VideoPlatform
    video_id: str