class TestFrameExtractor:
    def test_calculate_optimal_frame_count_short_video(self):
        from services.video_processor.frame_extractor import FrameExtractor
        
        frame_count = FrameExtractor.calculate_optimal_frame_count(
            duration=8.0,
            is_full_video=True
        )
        
        assert frame_count == 4
    
    def test_calculate_optimal_frame_count_medium_video(self):
        from services.video_processor.frame_extractor import FrameExtractor
        
        frame_count = FrameExtractor.calculate_optimal_frame_count(
            duration=25.0,
            is_full_video=True
        )
        
        assert frame_count == 8
    
    def test_calculate_optimal_frame_count_long_video(self):
        from services.video_processor.frame_extractor import FrameExtractor
        
        frame_count = FrameExtractor.calculate_optimal_frame_count(
            duration=100.0,
            is_full_video=True
        )
        
        assert frame_count == 12
    
    def test_calculate_optimal_frame_count_segmented_video(self):
        from services.video_processor.frame_extractor import FrameExtractor
        
        frame_count = FrameExtractor.calculate_optimal_frame_count(
            duration=100.0,
            is_full_video=False
        )
        
        assert frame_count == 2
    
    def test_default_frame_count(self):
        from services.video_processor.frame_extractor import FrameExtractor
        
        assert FrameExtractor.DEFAULT_FRAME_COUNT == 2