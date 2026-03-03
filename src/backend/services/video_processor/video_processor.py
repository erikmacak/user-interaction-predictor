import time
from typing import List, Tuple, Optional
from pathlib import Path

from domain.video import VideoSource, VideoPlatform
from services.video_processor.url_builder import VideoURLBuilder
from services.video_processor.segment_calculator import SegmentCalculator
from services.video_processor.downloader import VideoDownloader

class VideoProcessingResult:
    
    def __init__(
        self, 
        skipped: bool = False, 
        segments: List[Tuple[float, float]] = None,
        url: str = None,
        download_full: bool = False
    ):
        self.skipped = skipped
        self.segments = segments or []
        self.url = url
        self.download_full = download_full

class VideoProcessor:
    
    NO_SEGMENT_PLATFORMS = {VideoPlatform.TIKTOK}
    
    def __init__(self):
        self.downloader = VideoDownloader()
    
    def _should_force_full_download(self, platform: VideoPlatform, duration: float) -> bool:
        return platform in self.NO_SEGMENT_PLATFORMS
    
    def prepare_video_processing(
        self,
        video_source: VideoSource,
        duration: int,
        video_author: Optional[str] = None
    ) -> VideoProcessingResult:

        print(f"\n{'='*80}")
        print(f"🎬 Preparing video processing: {video_source.video_id}")
        print(f"📱 Platform: {video_source.platform.value}")
        print(f"👤 Author: {video_author or 'N/A'}")
        print(f"⏱️  Duration: {duration}s")
        print(f"{'='*80}\n")
        
        if SegmentCalculator.should_skip_video(duration):
            print(f"⏭️  SKIP: Video duration {duration}s is out of range (6-180s)\n")
            return VideoProcessingResult(skipped=True)
        
        url = VideoURLBuilder.build_url(video_source.platform, video_source.video_id, video_author)
        print(f"🔗 URL: {url}")
        
        force_full = self._should_force_full_download(video_source.platform, duration)
        
        if force_full:
            print(f"⚠️  Platform {video_source.platform.value} doesn't support segmentation")
        
        download_full = SegmentCalculator.should_download_full_video(duration) or force_full
        
        if download_full:
            reason = "short video" if duration < 20 else f"{video_source.platform.value} platform limitation"
            print(f"📥 Strategy: Download full video ({reason})")
            segments = [(0, duration)]
        else:
            segments = SegmentCalculator.calculate_segments(duration)
            print(f"🎞️  Strategy: Sequential segment download ({len(segments)} segments)")
        
        print(f"{'='*80}\n")
        
        return VideoProcessingResult(
            skipped=False,
            segments=segments,
            url=url,
            download_full=download_full
        )
    
    def download_segment(
        self,
        url: str,
        start_time: float,
        end_time: float,
        segment_number: int,
        total_segments: int,
        download_full: bool = False
    ) -> Tuple[str, float]:

        print(f"📥 Downloading segment {segment_number}/{total_segments} ({start_time:.1f}s - {end_time:.1f}s)")
        
        start = time.time()
        
        if download_full:
            video_path, duration = self.downloader.download_full_video(url)
        else:
            video_path, duration = self.downloader.download_segment(url, start_time, end_time)
        
        download_time = time.time() - start
        print(f"   ✓ Downloaded in {download_time:.2f}s")
        
        return video_path, duration