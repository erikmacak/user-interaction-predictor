from typing import List
from pydantic import BaseModel

from domain.video import VideoPlatform
from domain.action import PredictedActionType

class PredictActionsRequest(BaseModel):
    platform: VideoPlatform
    video_id: str

class PredictedAction(BaseModel):
    action: PredictedActionType

class PredictActionsResponse(BaseModel):
    predicted_actions: List[PredictedAction]