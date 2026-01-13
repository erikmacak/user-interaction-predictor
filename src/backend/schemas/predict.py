from typing import List
from pydantic import BaseModel, ConfigDict

from domain.video import VideoPlatform
from domain.action import PredictedActionType

class PredictActionsRequest(BaseModel):
    platform: VideoPlatform
    video_id: str

    model_config = ConfigDict(
        extra="forbid"
    )

class PredictedAction(BaseModel):
    action: PredictedActionType

class PredictActionsResponse(BaseModel):
    predicted_actions: List[PredictedAction]