from dataclasses import dataclass

@dataclass(frozen=True)
class SegmentConfig:
    segment_count: int
    segment_length: float
    frame_count: int

class SegmentCalculator:    
    CONFIGS = {
        "short": SegmentConfig(segment_count=2, segment_length=3.0, frame_count=2),
        "medium": SegmentConfig(segment_count=3, segment_length=4.0, frame_count=2),
        "long": SegmentConfig(segment_count=4, segment_length=5.0, frame_count=2),
    }
    
    MIN_DURATION = 6
    MAX_DURATION = 180
    
    @staticmethod
    def get_config(duration: float) -> SegmentConfig | None:
        if 6 <= duration < 20:
            return SegmentCalculator.CONFIGS["short"]
        elif 20 <= duration < 60:
            return SegmentCalculator.CONFIGS["medium"]
        elif 60 <= duration <= 180:
            return SegmentCalculator.CONFIGS["long"]
        return None
    
    @staticmethod
    def should_skip_video(duration: float) -> bool:
        return duration < SegmentCalculator.MIN_DURATION or duration > SegmentCalculator.MAX_DURATION
    
    @staticmethod
    def should_download_full_video(duration: float) -> bool:
        return False
    
    @staticmethod
    def calculate_segments(duration: float) -> list[tuple[float, float]]:
        if SegmentCalculator.should_skip_video(duration):
            raise ValueError(
                f"Video duration {duration}s is out of valid range "
                f"({SegmentCalculator.MIN_DURATION}-{SegmentCalculator.MAX_DURATION}s)"
            )
        
        config = SegmentCalculator.get_config(duration)
        
        if config is None:
            raise ValueError(f"No segment configuration found for duration {duration}s")
        
        segments = SegmentCalculator._build_segments_for_config(config, duration)
        
        return [(start, min(end, duration)) for start, end in segments]
    
    @staticmethod
    def _build_segments_for_config(config: SegmentConfig, duration: float) -> list[tuple[float, float]]:
        seg_len = config.segment_length
        
        if config.segment_count == 2:
            return SegmentCalculator._build_two_segments(duration, seg_len)
        elif config.segment_count == 3:
            return SegmentCalculator._build_three_segments(duration, seg_len)
        elif config.segment_count == 4:
            return SegmentCalculator._build_four_segments(duration, seg_len)
        
        return []
    
    @staticmethod
    def _build_two_segments(duration: float, seg_len: float) -> list[tuple[float, float]]:
        middle = duration / 2
        
        return [
            (1.0, min(1.0 + seg_len, duration)),
            (middle, min(middle + seg_len, duration))
        ]
    
    @staticmethod
    def _build_three_segments(duration: float, seg_len: float) -> list[tuple[float, float]]:
        middle = duration / 2
        quarter = duration / 4
        
        return [
            (1.0, min(1.0 + seg_len, duration)),
            (quarter, min(quarter + seg_len, duration)),
            (middle + 2, min(middle + 2 + seg_len, duration))
        ]
    
    @staticmethod
    def _build_four_segments(duration: float, seg_len: float) -> list[tuple[float, float]]:
        middle = duration / 2
        quarter = duration / 4
        three_quarter = (middle + duration) / 2
        
        return [
            (1.0, min(1.0 + seg_len, duration)),
            (quarter, min(quarter + seg_len, duration)),
            (middle + 3, min(middle + 3 + seg_len, duration)),
            (three_quarter, min(three_quarter + seg_len, duration))
        ]