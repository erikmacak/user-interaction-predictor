from dataclasses import dataclass

from domain.platform import VideoPlatform

@dataclass(frozen=True)
class VideoSource:
    platform: VideoPlatform
    video_id: str