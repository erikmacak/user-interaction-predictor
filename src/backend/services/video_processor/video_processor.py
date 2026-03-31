import time

from domain.platform import VideoPlatform
from domain.video import VideoSource
from services.video_processor.url_builder import VideoURLBuilder
from services.video_processor.segment_calculator import SegmentCalculator
from services.video_processor.downloader import VideoDownloader

class VideoProcessingResult:
    def __init__(
        self, 
        skipped: bool = False, 
        segments: list[tuple[float, float]] | None = None,
        url: str | None = None,
        download_full: bool = False
    ):
        self.skipped = skipped
        self.segments = segments or []
        self.url = url
        self.download_full = download_full

class VideoProcessor:
    NO_SEGMENT_PLATFORMS = {VideoPlatform.TIKTOK}
    
    SEPARATOR = "=" * 80
    
    def __init__(self):
        self.downloader = VideoDownloader()
    
    def prepare_video_processing(
        self,
        video_source: VideoSource,
        duration: int,
        video_author: str | None = None
    ) -> VideoProcessingResult:
        self._print_preparation_header(video_source, video_author)
        
        if SegmentCalculator.should_skip_video(duration):
            print(f"SKIP: Video duration {duration}s is out of range (6-180s)\n")
            return VideoProcessingResult(skipped=True)
        
        url = VideoURLBuilder.build_url(video_source.platform, video_source.video_id, video_author)
        print(f"URL: {url}")
        
        download_full = self._should_download_full_video(video_source.platform, duration)
        segments = self._calculate_segments(duration, download_full)
        
        self._print_strategy(video_source.platform, duration, download_full, len(segments))
        self._print_preparation_footer()
        
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
    ) -> tuple[str, float]:
        print(f" Downloading segment {segment_number}/{total_segments} ({start_time:.1f}s - {end_time:.1f}s)")
        
        start = time.time()
        
        if download_full:
            video_path, duration = self.downloader.download_full_video(url)
        else:
            video_path, duration = self.downloader.download_segment(url, start_time, end_time)
        
        download_time = time.time() - start
        print(f"    Downloaded in {download_time:.2f}s")
        
        return video_path, duration
    
    def _should_download_full_video(self, platform: VideoPlatform, duration: int) -> bool:
        force_full = self._should_force_full_download(platform)
        return SegmentCalculator.should_download_full_video(duration) or force_full
    
    def _should_force_full_download(self, platform: VideoPlatform) -> bool:
        return platform in self.NO_SEGMENT_PLATFORMS
    
    def _calculate_segments(
        self,
        duration: int,
        download_full: bool
    ) -> list[tuple[float, float]]:
        if download_full:
            return [(0, duration)]
        return SegmentCalculator.calculate_segments(duration)
    
    def _print_preparation_header(
        self,
        video_source: VideoSource,
        video_author: str | None
    ) -> None:
        print(f"\n{self.SEPARATOR}")
        print(f" Preparing video processing: {video_source.video_id}")
        print(f" Platform: {video_source.platform.value}")
        print(f" Author: {video_author or 'N/A'}")
        print(f"{self.SEPARATOR}\n")
    
    def _print_strategy(
        self,
        platform: VideoPlatform,
        duration: int,
        download_full: bool,
        segment_count: int
    ) -> None:
        if self._should_force_full_download(platform):
            print(f"Platform {platform.value} doesn't support segmentation")
        
        if download_full:
            reason = "short video" if duration < 20 else f"{platform.value} platform limitation"
            print(f"Strategy: Download full video ({reason})")
        else:
            print(f"Strategy: Sequential segment download ({segment_count} segments)")
    
    def _print_preparation_footer(self) -> None:
        print(f"{self.SEPARATOR}\n")