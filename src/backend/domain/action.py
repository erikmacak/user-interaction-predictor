from enum import Enum
from dataclasses import dataclass, replace

class PredictedActionType(str, Enum):
    LIKE = "like"
    SAVE = "save"
    SKIP = "skip"
    FINISH_WATCHING = "finish_watching"
    CONTINUE_WATCHING = "continue_watching"
    REWATCH = "rewatch"

@dataclass(frozen=True)
class PredictedAction:
    action_type: PredictedActionType
    seconds: int | None = None
    
    def to_string(self) -> str:
        if self.action_type == PredictedActionType.CONTINUE_WATCHING and self.seconds:
            return f"continue_watching_for: {self.seconds} seconds"
        return self.action_type.value
    
    def with_seconds(self, seconds: int) -> "PredictedAction":
        return replace(self, seconds=seconds)