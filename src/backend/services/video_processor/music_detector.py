import os
import sys
from contextlib import contextmanager
from dataclasses import dataclass

from shazamio import Shazam

@dataclass(frozen=True)
class MusicDetectionResult:
    detected: bool
    title: str | None = None
    artist: str | None = None
    
    def __str__(self) -> str:
        if self.detected:
            return f"{self.title} - {self.artist}"
        return "No music detected"

class MusicDetector:
    def __init__(self):
        self.shazam = Shazam()
    
    async def detect(self, video_path: str) -> MusicDetectionResult:
        try:
            with self._suppress_output():
                result = await self.shazam.recognize(video_path)
            
            return self._parse_shazam_result(result)
            
        except Exception:
            return MusicDetectionResult(detected=False)
    
    @staticmethod
    def _parse_shazam_result(result: dict) -> MusicDetectionResult:
        if result and 'track' in result:
            track = result['track']
            title = track.get('title', 'Unknown')
            artist = track.get('subtitle', 'Unknown Artist')
            
            return MusicDetectionResult(
                detected=True,
                title=title,
                artist=artist
            )
        
        return MusicDetectionResult(detected=False)
    
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