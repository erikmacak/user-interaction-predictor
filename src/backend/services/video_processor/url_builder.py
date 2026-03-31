from domain.platform import VideoPlatform

class VideoURLBuilder:
    @staticmethod
    def build_url(
        platform: VideoPlatform,
        video_id: str,
        video_author: str | None = None
    ) -> str:
        url_builders = {
            VideoPlatform.YOUTUBE: VideoURLBuilder._build_youtube_url,
            VideoPlatform.TIKTOK: VideoURLBuilder._build_tiktok_url,
            VideoPlatform.INSTAGRAM: VideoURLBuilder._build_instagram_url,
        }
        
        builder = url_builders.get(platform)
        
        if builder is None:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return builder(video_id, video_author)
    
    @staticmethod
    def _build_youtube_url(video_id: str, video_author: str | None = None) -> str:
        return f"https://www.youtube.com/shorts/{video_id}"
    
    @staticmethod
    def _build_tiktok_url(video_id: str, video_author: str | None = None) -> str:
        if not video_author:
            raise ValueError("video_author is required for TikTok URLs")
        return f"https://www.tiktok.com/@{video_author}/video/{video_id}"
    
    @staticmethod
    def _build_instagram_url(video_id: str, video_author: str | None = None) -> str:
        return f"https://www.instagram.com/reel/{video_id}/"