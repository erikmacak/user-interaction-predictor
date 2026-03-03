import cv2
import base64
from io import BytesIO
from PIL import Image
from typing import List
import os

class FrameExtractor:
    
    @staticmethod
    def extract_frames(
        video_path: str,
        frame_count: int = 2,
        start_time: float = None,
        end_time: float = None
    ) -> List[str]:
        frame_count = int(frame_count)
        
        os.environ['OPENCV_VIDEOIO_DEBUG'] = '0'
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if start_time is None or end_time is None:
            start_frame = 0
            end_frame = total_video_frames
        else:
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
        
        start_frame = max(0, min(start_frame, total_video_frames - 1))
        end_frame = max(start_frame + 1, min(end_frame, total_video_frames))
        
        frames_to_extract = end_frame - start_frame
        
        if frames_to_extract <= 0:
            cap.release()
            return []
        
        actual_frame_count = min(frame_count, frames_to_extract)
        step = max(1, frames_to_extract // actual_frame_count)
        
        base64_frames = []
        
        for i in range(actual_frame_count):
            frame_number = start_frame + (i * step)
            
            if frame_number >= total_video_frames:
                break
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            pil_image = Image.fromarray(frame_rgb)

            pil_image.thumbnail((640, 640), Image.Resampling.LANCZOS)
            
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG", quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            base64_frames.append(img_base64)
        
        cap.release()
        
        return base64_frames