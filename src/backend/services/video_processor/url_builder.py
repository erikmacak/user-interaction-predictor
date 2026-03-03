from domain.video import VideoPlatform
from typing import Optional

class VideoURLBuilder:
    
    @staticmethod
    def build_url(platform: VideoPlatform, video_id: str, video_author: Optional[str] = None) -> str:
        if platform == VideoPlatform.YOUTUBE:
            return f"https://www.youtube.com/shorts/{video_id}"
        
        elif platform == VideoPlatform.TIKTOK:
            if not video_author:
                raise ValueError("video_author is required for TikTok URLs")
            return f"https://www.tiktok.com/@{video_author}/video/{video_id}"
        
        elif platform == VideoPlatform.INSTAGRAM:
            return f"https://www.instagram.com/reel/{video_id}/"
        
        else:
            raise ValueError(f"Unsupported platform: {platform}")