import os
import sys
import tempfile
import time
from pathlib import Path
from contextlib import contextmanager

import yt_dlp

from domain.errors import VideoDownloadError as DomainVideoDownloadError

class VideoDownloader:
    DEFAULT_FORMAT = 'worst[height<=360]/worst[height<=480]/worst/best'
    SIMPLE_FORMAT = 'best/worst'
    
    @staticmethod
    def download_full_video(url: str) -> tuple[str, float]:
        output_dir = VideoDownloader._get_ram_disk_path()
        output_template = str(output_dir / "%(id)s.%(ext)s")
        
        ydl_opts = VideoDownloader._get_ydl_opts(url, output_template)
        
        start_time = time.time()
        
        try:
            with VideoDownloader._suppress_output():
                video_path, duration = VideoDownloader._download_with_ydl(url, ydl_opts)
            
            download_time = time.time() - start_time
            print(f" Downloaded in {download_time:.2f}s")
            
            return video_path, duration
            
        except Exception as e:
            VideoDownloader._raise_domain_error(url, e)
    
    @staticmethod
    def download_segment(url: str, start_time: float, end_time: float) -> tuple[str, float]:
        output_dir = VideoDownloader._get_ram_disk_path()
        start_int = int(time.time() * 10000)
        output_template = str(output_dir / f"%(id)s_seg_{start_int}.%(ext)s")
        
        duration = end_time - start_time
        
        ydl_opts = VideoDownloader._get_ydl_opts(url, output_template)
        VideoDownloader._add_download_range(ydl_opts, start_time, end_time)
        
        segment_start = time.time()
        
        try:
            with VideoDownloader._suppress_output():
                video_path, _ = VideoDownloader._download_with_ydl(url, ydl_opts)
            
            return video_path, duration
            
        except Exception:
            try:
                return VideoDownloader.download_full_video(url)
            except DomainVideoDownloadError:
                raise
    
    @staticmethod
    def _download_with_ydl(url: str, ydl_opts: dict) -> tuple[str, float]:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            duration = info.get('duration', 0)
        
        return video_path, duration
    
    @staticmethod
    def _get_ram_disk_path() -> Path:
        ram_disk = Path("/dev/shm")
        return ram_disk if ram_disk.exists() else Path(tempfile.gettempdir())
    
    @staticmethod
    def _get_ydl_opts(url: str, output_template: str) -> dict:
        base_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            'no_color': True,
            'extract_flat': False,
            'logger': None,
            'no_progress': True,
            'postprocessor_args': {
                'ffmpeg': [
                    '-hide_banner',
                    '-loglevel', 'panic',
                    '-nostats'
                ]
            },
        }
        
        base_opts['format'] = VideoDownloader._get_format_for_url(url)
        
        return base_opts
    
    @staticmethod
    def _get_format_for_url(url: str) -> str:
        if 'instagram.com' in url or 'tiktok.com' in url:
            return VideoDownloader.SIMPLE_FORMAT
        return VideoDownloader.DEFAULT_FORMAT
    
    @staticmethod
    def _add_download_range(ydl_opts: dict, start_time: float, end_time: float) -> None:
        try:
            ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(
                None, 
                [(start_time, end_time)]
            )
        except AttributeError:
            pass
    
    @staticmethod
    @contextmanager
    def _suppress_output():
        devnull = open(os.devnull, 'w')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
    
    @staticmethod
    def _raise_domain_error(url: str, error: Exception) -> None:
        platform = VideoDownloader._extract_platform_from_url(url)
        video_id = VideoDownloader._extract_video_id_from_url(url)
        reason = VideoDownloader._parse_download_error(str(error))
        
        raise DomainVideoDownloadError(platform, video_id, reason)
    
    @staticmethod
    def _extract_platform_from_url(url: str) -> str:
        platform_map = {
            'youtube.com': 'YouTube',
            'youtu.be': 'YouTube',
            'tiktok.com': 'TikTok',
            'instagram.com': 'Instagram',
        }
        
        for key, platform in platform_map.items():
            if key in url:
                return platform
        
        return 'Unknown'
    
    @staticmethod
    def _extract_video_id_from_url(url: str) -> str:
        return url.split('/')[-1].split('?')[0]
    
    @staticmethod
    def _parse_download_error(error_msg: str) -> str:
        error_lower = error_msg.lower()
        
        error_patterns = {
            ('unavailable', 'does not exist'): "Video does not exist or is unavailable",
            ('private',): "Video is private",
            ('blocked', 'ip address'): "Access blocked (geo-restriction or IP block)",
            ('empty media response', 'login'): "Video requires authentication or does not exist",
            ('copyright',): "Video removed due to copyright",
            ('age', 'restricted'): "Video is age-restricted",
        }
        
        for patterns, message in error_patterns.items():
            if all(pattern in error_lower for pattern in patterns):
                return message
        
        return "Video download failed"