class TestSegmentCalculator:
    def test_should_skip_video_too_short(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        assert SegmentCalculator.should_skip_video(5)
    
    def test_should_skip_video_too_long(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        assert SegmentCalculator.should_skip_video(181)
    
    def test_should_not_skip_valid_video(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        assert not SegmentCalculator.should_skip_video(30)
        assert not SegmentCalculator.should_skip_video(6)
        assert not SegmentCalculator.should_skip_video(180)
    
    def test_should_download_full_video_short(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        assert not SegmentCalculator.should_download_full_video(15)
    
    def test_should_not_download_full_video_medium(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        assert not SegmentCalculator.should_download_full_video(40)

    def test_calculate_segments_two_segments(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        segments = SegmentCalculator.calculate_segments(15)
        
        assert len(segments) == 2
    
    def test_calculate_segments_three_segments(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        segments = SegmentCalculator.calculate_segments(30)
        
        assert len(segments) == 3
    
    def test_calculate_segments_four_segments(self):
        from services.video_processor.segment_calculator import SegmentCalculator
        
        segments = SegmentCalculator.calculate_segments(120)
        
        assert len(segments) == 4