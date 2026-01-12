from dataclasses import dataclass
from enum import Enum

class VideoPlatform(str, Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"

@dataclass(frozen=True)
class VideoSource:
    platform: VideoPlatform
    video_id: str