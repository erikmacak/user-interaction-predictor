from abc import ABC, abstractmethod

from domain.video import VideoSource
from domain.action import PredictedActionType

class BasePredictor(ABC):
    def predict(self, video_source: VideoSource) -> list[PredictedActionType]:
        data = self._extract_data(video_source)
        return self._predict_from_data(data)
    
    def _extract_data(self, video_source: VideoSource) -> dict:
        return {
            "platform": video_source.platform.value,
            "video_id": video_source.video_id,
        }
    
    @abstractmethod
    def _predict_from_data(self, data: dict) -> list[PredictedActionType]:
        raise NotImplementedError("Subclasses must implement _predict_from_data")