from abc import ABC, abstractmethod

from domain.video import VideoSource

class BaseVideoAvailabilityService(ABC):
    @abstractmethod
    def exists(self, video: VideoSource) -> bool:
        raise NotImplementedError