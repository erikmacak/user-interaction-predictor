import asyncio
import time
from dataclasses import dataclass

from services.video_processor.frame_extractor import FrameExtractor
from services.video_processor.music_detector import MusicDetector, MusicDetectionResult
from services.ai.ai_analyzer import AIAnalyzer, AIAnalysisResult
from services.ai.ai_limiter import AILimiter

@dataclass(frozen=True)
class SegmentAnalysisResult:
    segment_number: int
    start_time: float
    end_time: float
    frames_base64: list[str]
    music: MusicDetectionResult
    ai_analysis: AIAnalysisResult
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time


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
        description: str | None,
        hashtags: list[str] | None,
        user_state_json: str,
        is_full_video: bool = False,
    ) -> SegmentAnalysisResult:
        print(f"    Deep Analysis in progress")
        
        analysis_start = time.time()
        
        frame_count = FrameExtractor.calculate_optimal_frame_count(
            duration=duration,
            is_full_video=is_full_video
        )
        
        if is_full_video:
            print(f"       Full video strategy: Extracting {frame_count} frames")
        
        frames, music = await self._extract_media_features(video_file, frame_count)
        
        self._log_extraction_results(frames, music)
        
        ai_result = await self._analyze_with_ai(
            segment_number=segment_number,
            frames=frames,
            music=music,
            description=description,
            hashtags=hashtags,
            user_state_json=user_state_json
        )
        
        analysis_time = time.time() - analysis_start
        
        self._log_analysis_summary(start_time, end_time, analysis_time)
        
        return SegmentAnalysisResult(
            segment_number=segment_number,
            start_time=start_time,
            end_time=end_time,
            frames_base64=frames,
            music=music,
            ai_analysis=ai_result
        )
    
    async def _extract_media_features(
        self,
        video_file: str,
        frame_count: int
    ) -> tuple[list[str], MusicDetectionResult]:
        frames_task = asyncio.create_task(
            self._extract_frames_async(video_file, frame_count)
        )
        music_task = asyncio.create_task(
            self._detect_music_async(video_file)
        )
        
        return await asyncio.gather(frames_task, music_task)
    
    async def _extract_frames_async(
        self,
        video_file: str,
        frame_count: int
    ) -> list[str]:
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
    
    async def _analyze_with_ai(
        self,
        segment_number: int,
        frames: list[str],
        music: MusicDetectionResult,
        description: str | None,
        hashtags: list[str] | None,
        user_state_json: str
    ) -> AIAnalysisResult:
        music_str = str(music) if music.detected else None
        
        return await AILimiter.execute(
            self.ai_analyzer.analyze_segment(
                segment_number=segment_number,
                frames_base64=frames,
                description=description,
                hashtags=hashtags,
                music=music_str,
                user_state_json=user_state_json
            )
        )
    
    @staticmethod
    def _log_extraction_results(frames: list[str], music: MusicDetectionResult) -> None:
        print(f"       Frames extracted: {len(frames)} frames")
        print(f"       Music: {music}")
    
    @staticmethod
    def _log_analysis_summary(start_time: float, end_time: float, analysis_time: float) -> None:
        print(f"       Segment duration: {end_time - start_time:.1f}s\n")
        print(f"       Total analysis time: {analysis_time:.2f}s\n")