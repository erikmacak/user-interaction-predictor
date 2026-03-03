import yt_dlp
import tempfile
import time
import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple

class VideoDownloadError(Exception):
    pass

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
            print(f"✅ Downloaded in {download_time:.2f}s")
            
            return video_path, duration
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            raise VideoDownloadError(f"Failed to download video: {e}")
    
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
            print(f"✅ Downloaded segment in {download_time:.2f}s")
            
            return video_path, duration
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            return VideoDownloader.download_full_video(url)