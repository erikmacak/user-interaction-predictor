import yt_dlp
import tempfile
import time
import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple

from domain.errors import VideoDownloadError as DomainVideoDownloadError

class VideoDownloader:
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
        
        if 'instagram.com' in url:
            base_opts['format'] = 'best/worst'
        elif 'tiktok.com' in url:
            base_opts['format'] = 'best/worst'
        else:
            base_opts['format'] = 'worst[height<=360]/worst[height<=480]/worst/best'
        
        return base_opts
    
    @staticmethod
    def _extract_platform_from_url(url: str) -> str:
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'YouTube'
        elif 'tiktok.com' in url:
            return 'TikTok'
        elif 'instagram.com' in url:
            return 'Instagram'
        return 'Unknown'
    
    @staticmethod
    def _extract_video_id_from_url(url: str) -> str:
        return url.split('/')[-1].split('?')[0]
    
    @staticmethod
    def _parse_download_error(error_msg: str) -> str:
        error_lower = error_msg.lower()
        
        if 'unavailable' in error_lower or 'does not exist' in error_lower:
            return "Video does not exist or is unavailable"
        elif 'private' in error_lower:
            return "Video is private"
        elif 'blocked' in error_lower or 'ip address' in error_lower:
            return "Access blocked (geo-restriction or IP block)"
        elif 'empty media response' in error_lower or 'login' in error_lower:
            return "Video requires authentication or does not exist"
        elif 'copyright' in error_lower:
            return "Video removed due to copyright"
        elif 'age' in error_lower and 'restricted' in error_lower:
            return "Video is age-restricted"
        else:
            return "Video download failed"
    
    @staticmethod
    def download_full_video(url: str) -> Tuple[str, float]:
        output_dir = VideoDownloader._get_ram_disk_path()
        output_template = str(output_dir / "%(id)s.%(ext)s")
        
        ydl_opts = VideoDownloader._get_ydl_opts(url, output_template)
        
        start_time = time.time()
        
        devnull = open(os.devnull, 'w')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                duration = info.get('duration', 0)
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
            download_time = time.time() - start_time
            print(f" Downloaded in {download_time:.2f}s")
            
            return video_path, duration
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
            platform = VideoDownloader._extract_platform_from_url(url)
            video_id = VideoDownloader._extract_video_id_from_url(url)
            reason = VideoDownloader._parse_download_error(str(e))
            
            raise DomainVideoDownloadError(platform, video_id, reason)
    
    @staticmethod
    def download_segment(url: str, start_time: float, end_time: float) -> Tuple[str, float]:
        output_dir = VideoDownloader._get_ram_disk_path()
        start_int = int(time.time() * 10000)
        output_template = str(output_dir / f"%(id)s_seg_{start_int}.%(ext)s")
        
        duration = end_time - start_time
        
        ydl_opts = VideoDownloader._get_ydl_opts(url, output_template)
        
        try:
            ydl_opts['download_ranges'] = yt_dlp.utils.download_range_func(
                None, 
                [(start_time, end_time)]
            )
        except AttributeError:
            pass
        
        segment_start = time.time()
        
        devnull = open(os.devnull, 'w')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
            download_time = time.time() - segment_start
            print(f" Downloaded segment in {download_time:.2f}s")
            
            return video_path, duration
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
            try:
                return VideoDownloader.download_full_video(url)
            except DomainVideoDownloadError:
                raise