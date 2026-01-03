from abc import ABC, abstractmethod
from typing import Any

from domain.video import VideoSource

class BasePredictor(ABC):
    def predict(self, video_source: VideoSource) -> str:
        data = self._extract_data(video_source)
        return self._predict_from_data(data)

    def _extract_data(self, video_source: VideoSource) -> Any:
        return {
            "platform": video_source.platform,
            "video_id": video_source.video_id,
        }

    @abstractmethod
    def _predict_from_data(self, data: Any) -> str:
        raise NotImplementedError
