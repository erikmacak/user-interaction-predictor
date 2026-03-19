import asyncio
import time
from typing import List, Optional
from dataclasses import dataclass

from services.video_processor.frame_extractor import FrameExtractor
from services.video_processor.music_detector import MusicDetector, MusicDetectionResult
from services.video_processor.segment_calculator import SegmentCalculator
from services.ai.ai_analyzer import AIAnalyzer, AIAnalysisResult
from services.ai.ai_limiter import AILimiter

@dataclass
class SegmentAnalysisResult:
    segment_number: int
    start_time: float
    end_time: float
    frames_base64: List[str]
    music: MusicDetectionResult
    ai_analysis: AIAnalysisResult
    
class SegmentAnalyzer:
    
    def __init__(self):
        self.frame_extractor = FrameExtractor()
        self.music_detector = MusicDetector()
        self.ai_analyzer = AIAnalyzer()
    
    async def analyze(
        self,
        video_file: str,
        segment_number: int,
        start_time: float,
        end_time: float,
        duration: float,
        description: Optional[str],
        hashtags: Optional[List[str]],
        user_state_json: str
    ) -> SegmentAnalysisResult:
        
        print(f"    Deep Analysis in progress")
        
        analysis_start = time.time()
        
        config = SegmentCalculator.get_config(duration)
        frame_count = 2
        
        frames_task = asyncio.create_task(
            self._extract_frames_async(video_file, frame_count)
        )
        music_task = asyncio.create_task(
            self._detect_music_async(video_file)
        )
        
        frames, music = await asyncio.gather(frames_task, music_task)
        
        print(f"        Frames extracted: {len(frames)} frames")
        print(f"       Music: {music}")
        
        music_str = str(music) if music.detected else None
        
        ai_result = await AILimiter.execute(
            self.ai_analyzer.analyze_segment(
                segment_number=segment_number,
                frames_base64=frames,
                description=description,
                hashtags=hashtags,
                music=music_str,
                user_state_json=user_state_json
            )
        )
        
        analysis_time = time.time() - analysis_start
        
        print(f"       Segment duration: {end_time - start_time:.1f}s")
        print(f"       Total analysis time: {analysis_time:.2f}s\n")
        
        return SegmentAnalysisResult(
            segment_number=segment_number,
            start_time=start_time,
            end_time=end_time,
            frames_base64=frames,
            music=music,
            ai_analysis=ai_result
        )
    
    async def _extract_frames_async(
        self,
        video_file: str,
        frame_count: int
    ) -> List[str]:
        loop = asyncio.get_event_loop()
        
        return await loop.run_in_executor(
            None,
            self.frame_extractor.extract_frames,
            video_file,
            frame_count,
            None,
            None
        )
    
    async def _detect_music_async(self, video_file: str) -> MusicDetectionResult:
        return await self.music_detector.detect(video_file)