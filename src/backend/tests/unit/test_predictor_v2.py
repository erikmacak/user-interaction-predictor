from domain.platform import VideoPlatform

class TestPredictorV2:
    def test_no_segment_platforms(self):
        from services.predictor.v2 import PredictorV2
        
        predictor = PredictorV2()
        
        assert VideoPlatform.TIKTOK in predictor.NO_SEGMENT_PLATFORMS
    
    def test_duration_validation(self):
        from services.predictor.v2 import PredictorV2
        
        assert PredictorV2.MIN_DURATION == 6
        assert PredictorV2.MAX_DURATION == 180
        
        assert PredictorV2._is_duration_in_range(10)
        assert PredictorV2._is_duration_in_range(6)
        assert PredictorV2._is_duration_in_range(180)
        
        assert not PredictorV2._is_duration_in_range(5)
        assert not PredictorV2._is_duration_in_range(181)
        assert not PredictorV2._is_duration_in_range(0)
    
    def test_should_use_full_video_strategy_for_tiktok(self):
        from services.predictor.v2 import PredictorV2
        
        predictor = PredictorV2()
        
        assert predictor._should_use_full_video_strategy(
            VideoPlatform.TIKTOK,
            download_full=False
        )
    
    def test_should_use_full_video_strategy_for_download_full(self):
        from services.predictor.v2 import PredictorV2
        
        predictor = PredictorV2()
        
        assert predictor._should_use_full_video_strategy(
            VideoPlatform.YOUTUBE,
            download_full=True
        )
    
    def test_should_not_use_full_video_strategy_for_youtube(self):
        from services.predictor.v2 import PredictorV2
        
        predictor = PredictorV2()
        
        assert not predictor._should_use_full_video_strategy(
            VideoPlatform.YOUTUBE,
            download_full=False
        )
    
    def test_should_not_use_full_video_strategy_for_instagram(self):
        from services.predictor.v2 import PredictorV2
        
        predictor = PredictorV2()
        
        assert not predictor._should_use_full_video_strategy(
            VideoPlatform.INSTAGRAM,
            download_full=False
        )