import re
from urllib.parse import urlparse

from domain.video import VideoPlatform, VideoSource

class VideoParserService:
    _INSTAGRAM_REGEX = re.compile(r"/reels?/([A-Za-z0-9_-]{5,})")
    _TIKTOK_REGEX = re.compile(r"/video/(\d+)")
    _YOUTUBE_REGEX = re.compile(r"/shorts/([A-Za-z0-9_-]{11})")

    @classmethod
    def parse(cls, url: str) -> VideoSource:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        if "instagram.com" in domain:
            return cls._parse_instagram(url)

        if "tiktok.com" in domain:
            return cls._parse_tiktok(url)

        if "youtube.com" in domain or "youtu.be" in domain:
            return cls._parse_youtube(url)

        raise ValueError("Unsupported video platform")

    @classmethod
    def _parse_instagram(cls, url: str) -> VideoSource:
        match = cls._INSTAGRAM_REGEX.search(url)
        if not match:
            raise ValueError("Invalid Instagram video URL")

        video_id = match.group(1)
        return VideoSource(
            platform=VideoPlatform.INSTAGRAM,
            video_id=video_id,
            canonical_url=url,
        )

    @classmethod
    def _parse_tiktok(cls, url: str) -> VideoSource:
        match = cls._TIKTOK_REGEX.search(url)
        if not match:
            raise ValueError("Invalid TikTok video URL")

        video_id = match.group(1)
        return VideoSource(
            platform=VideoPlatform.TIKTOK,
            video_id=video_id,
            canonical_url=url,
        )

    @classmethod
    def _parse_youtube(cls, url: str) -> VideoSource:
        match = cls._YOUTUBE_REGEX.search(url)
        if not match:
            raise ValueError("Invalid YouTube Shorts URL")

        video_id = match.group(1)
        return VideoSource(
            platform=VideoPlatform.YOUTUBE,
            video_id=video_id,
            canonical_url=url,
        )