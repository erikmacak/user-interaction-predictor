from abc import ABC, abstractmethod
from typing import Any, List
from domain.video import VideoSource, VideoPlatform
from domain.action import PredictedActionType
from services.video_availability.registry import VideoAvailabilityRegistry
from domain.errors import VideoNotFoundError

class BasePredictor(ABC):
    def predict(
        self, 
        video_source: VideoSource, 
        check_video_existence: bool = True
    ) -> List[PredictedActionType]:
        
        if check_video_existence:
            if not VideoAvailabilityRegistry.exists(video_source):
                raise VideoNotFoundError(video_source.platform)
        
        data = self._extract_data(video_source)
        return self._predict_from_data(data)
    
    def _extract_data(self, video_source: VideoSource) -> Any:
        return {
            "platform": video_source.platform,
            "video_id": video_source.video_id,
        }
    
    @abstractmethod
    def _predict_from_data(self, data: Any) -> List[PredictedActionType]:
        raise NotImplementedError