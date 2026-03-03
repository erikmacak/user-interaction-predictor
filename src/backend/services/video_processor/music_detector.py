import os
import sys
from shazamio import Shazam
from typing import Optional

class MusicDetectionResult:
    
    def __init__(self, detected: bool, title: str = None, artist: str = None):
        self.detected = detected
        self.title = title
        self.artist = artist
    
    def __str__(self):
        if self.detected:
            return f"{self.title} - {self.artist}"
        return "No music detected"

class MusicDetector:
    
    def __init__(self):
        self.shazam = Shazam()
    
    async def detect(self, video_path: str) -> MusicDetectionResult:

        devnull = open(os.devnull, 'w')
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            
            result = await self.shazam.recognize(video_path)
            
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
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
            
        except Exception as e:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            devnull.close()
            
            return MusicDetectionResult(detected=False)