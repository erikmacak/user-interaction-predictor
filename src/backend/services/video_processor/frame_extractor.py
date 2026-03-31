import os
import base64
from io import BytesIO

import cv2
from PIL import Image

class FrameExtractor:
    DEFAULT_FRAME_COUNT = 2
    MAX_DIMENSION = 640
    JPEG_QUALITY = 85
    
    @staticmethod
    def calculate_optimal_frame_count(duration: float, is_full_video: bool = False) -> int:
        if not is_full_video:
            return FrameExtractor.DEFAULT_FRAME_COUNT
        
        if duration < 10:
            return 4
        elif duration <= 20:
            return 6
        elif duration <= 40:
            return 8
        elif duration <= 60:
            return 10
        else:
            return 12
    
    @staticmethod
    def extract_frames(
        video_path: str,
        frame_count: int = DEFAULT_FRAME_COUNT,
        start_time: float | None = None,
        end_time: float | None = None
    ) -> list[str]:
        os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            start_frame, end_frame = FrameExtractor._calculate_frame_range(
                start_time, end_time, fps, total_frames
            )
            
            frames_to_extract = end_frame - start_frame
            
            if frames_to_extract <= 0:
                return []
            
            base64_frames = FrameExtractor._extract_frame_sequence(
                cap, start_frame, end_frame, frame_count, total_frames
            )
            
            return base64_frames
        finally:
            cap.release()
    
    @staticmethod
    def _calculate_frame_range(
        start_time: float | None,
        end_time: float | None,
        fps: float,
        total_frames: int
    ) -> tuple[int, int]:
        if start_time is None or end_time is None:
            return 0, total_frames
        
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps)
        
        start_frame = max(0, min(start_frame, total_frames - 1))
        end_frame = max(start_frame + 1, min(end_frame, total_frames))
        
        return start_frame, end_frame
    
    @staticmethod
    def _extract_frame_sequence(
        cap: cv2.VideoCapture,
        start_frame: int,
        end_frame: int,
        requested_count: int,
        total_frames: int
    ) -> list[str]:
        frames_to_extract = end_frame - start_frame
        actual_frame_count = min(requested_count, frames_to_extract)
        step = max(1, frames_to_extract // actual_frame_count)
        
        base64_frames = []
        
        for i in range(actual_frame_count):
            frame_number = start_frame + (i * step)
            
            if frame_number >= total_frames:
                break
            
            frame_base64 = FrameExtractor._extract_single_frame(cap, frame_number)
            
            if frame_base64:
                base64_frames.append(frame_base64)
        
        return base64_frames
    
    @staticmethod
    def _extract_single_frame(cap: cv2.VideoCapture, frame_number: int) -> str | None:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        if not ret:
            return None
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        
        pil_image.thumbnail(
            (FrameExtractor.MAX_DIMENSION, FrameExtractor.MAX_DIMENSION),
            Image.Resampling.LANCZOS
        )
        
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG", quality=FrameExtractor.JPEG_QUALITY)
        
        return base64.b64encode(buffered.getvalue()).decode('utf-8')