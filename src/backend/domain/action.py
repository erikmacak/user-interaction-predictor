from enum import Enum

class PredictedActionType(str, Enum):
    SKIP = "skip"
    LIKE = "like"
    REWATCH = "rewatch"
    FINISH_WATCHING = "finish_watching"
    FOLLOW = "follow"
    SAVE = "save"